import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from api.agent import orchestrator, tools
from api.index import orchestrator_endpoint
from api.models import OrchestratorRequest


class FakeEmbeddings:
    def __init__(self):
        self.document_texts = []
        self.queries = []

    def embed_documents(self, texts):
        self.document_texts.extend(texts)
        return [
            [0.0, 1.0]
            if "housing" in text.lower()
            else ([1.0, 0.0] if "tamil scholarship" in text.lower() else [0.8, 0.6])
            for text in texts
        ]

    def embed_query(self, text):
        self.queries.append(text)
        return [1.0, 0.0]


class FakeChatModel:
    def __init__(self, response_text):
        self.response_text = response_text
        self.messages = None

    def invoke(self, messages):
        self.messages = messages
        return SimpleNamespace(content=self.response_text)


class VectorSearchTests(unittest.TestCase):
    def test_embeddings_rank_only_selected_state_and_all_india_candidates(self):
        catalog = [
            {
                "id": "tn-scholarship",
                "state": "Tamil Nadu",
                "nameEn": "Tamil Scholarship",
                "category": "EDUCATION",
            },
            {
                "id": "central-scholarship",
                "state": "All India",
                "nameEn": "National Scholarship",
                "category": "EDUCATION",
            },
            {
                "id": "tn-housing",
                "state": "Tamil Nadu",
                "nameEn": "Tamil Nadu Housing Support",
                "category": "HOUSING",
            },
            {
                "id": "ka-farmer",
                "state": "Karnataka",
                "nameEn": "Farmer Support",
                "category": "AGRICULTURE",
            },
        ]
        embeddings = FakeEmbeddings()
        with (
            patch.object(tools, "load_schemes_catalog", return_value=catalog),
            patch.object(tools, "_get_embedding_client", return_value=embeddings),
            patch.object(tools, "_SCHEME_EMBEDDINGS", {}),
        ):
            results = tools.search_in_memory_schemes(
                "graduate education scholarship",
                state="Tamil Nadu",
                top_k=10,
                min_score=0.3,
            )

        self.assertEqual(
            [scheme["id"] for scheme in results],
            ["tn-scholarship", "central-scholarship"],
        )
        self.assertEqual(len(embeddings.document_texts), 3)
        self.assertTrue(all("farmer support" not in text.lower() for text in embeddings.document_texts))
        self.assertNotIn("tn-housing", [scheme["id"] for scheme in results])
        self.assertGreater(results[0]["score"], results[1]["score"])

    def test_top_k_caps_candidates_and_cached_catalog_is_not_reembedded(self):
        catalog = [
            {
                "id": "tn-one",
                "state": "Tamil Nadu",
                "nameEn": "Tamil Scholarship",
                "category": "EDUCATION",
            },
            {
                "id": "tn-two",
                "state": "Tamil Nadu",
                "nameEn": "Tamil Scholarship",
                "category": "EDUCATION",
            },
        ]
        embeddings = FakeEmbeddings()
        with (
            patch.object(tools, "load_schemes_catalog", return_value=catalog),
            patch.object(tools, "_get_embedding_client", return_value=embeddings),
            patch.object(tools, "_SCHEME_EMBEDDINGS", {}),
        ):
            first = tools.search_in_memory_schemes("scholarship", state="Tamil Nadu", top_k=1)
            second = tools.search_in_memory_schemes("scholarship", state="Tamil Nadu", top_k=1)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(len(embeddings.document_texts), 2)
        self.assertEqual(len(embeddings.queries), 2)

    def test_gemini_reranks_only_shortlist_and_receives_no_sensitive_profile_fields(self):
        profile = {
            "name": "Private Name",
            "state": "Tamil Nadu",
            "educationLevel": "GRADUATE",
            "occupation": "UNEMPLOYED",
            "familyAnnualIncome": 50000,
            "casteCategory": "SC",
            "disabilityPercentage": 40,
        }
        candidates = [
            {
                "id": "tn-job",
                "state": "Tamil Nadu",
                "nameEn": "Graduate Employment Support",
                "category": "EMPLOYMENT",
                "benefitSummaryEn": "Training and job assistance",
                "eligibilityCriteria": [],
            },
            {
                "id": "tn-scholarship",
                "state": "Tamil Nadu",
                "nameEn": "Higher Education Scholarship",
                "category": "EDUCATION",
                "benefitSummaryEn": "Support for higher education",
                "eligibilityCriteria": [],
            },
        ]
        model = FakeChatModel('{"rankedSchemeIds":["tn-job"]}')
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch.object(orchestrator, "_get_gemini_chat_model", return_value=model),
        ):
            with self.assertLogs("api.agent.orchestrator", level="INFO") as captured:
                ranked, status = orchestrator._rank_candidates_with_gemini(profile, candidates)

        self.assertEqual(status, "RERANKED")
        self.assertEqual([scheme["id"] for scheme in ranked], ["tn-job"])
        prompt = model.messages[1].content
        self.assertIn("tn-scholarship", prompt)
        self.assertIn("GRADUATE", prompt)
        self.assertIn("UNEMPLOYED", prompt)
        for sensitive_value in ("Private Name", "50000", '"SC"', "40"):
            self.assertNotIn(sensitive_value, prompt)
        self.assertTrue(any("GeminiSchemeReranker request" in line for line in captured.output))
        self.assertTrue(any("GeminiSchemeReranker response" in line for line in captured.output))

    def test_gemini_invalid_response_does_not_return_unreranked_candidates(self):
        candidates = [{"id": "tn-one"}, {"id": "tn-two"}]
        model = FakeChatModel("not json")
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch.object(orchestrator, "_get_gemini_chat_model", return_value=model),
        ):
            ranked, status = orchestrator._rank_candidates_with_gemini(
                {"educationLevel": "GRADUATE"},
                candidates,
            )

        self.assertEqual(status, "RERANKER_INVALID_RESPONSE")
        self.assertEqual(ranked, [])

    def test_orchestrator_fails_closed_when_gemini_reranking_fails(self):
        candidates = [{"id": "tn-job", "state": "Tamil Nadu", "eligibilityMode": "MANUAL_REVIEW"}]
        with (
            patch("api.agent.orchestrator.search_in_memory_schemes", return_value=candidates),
            patch(
                "api.agent.orchestrator._rank_candidates_with_gemini",
                return_value=([], "RERANKER_ERROR"),
            ),
        ):
            with self.assertRaises(tools.VectorSearchError):
                orchestrator.run_orchestration_swarm(
                    {"state": "Tamil Nadu", "educationLevel": "GRADUATE", "occupation": "UNEMPLOYED"}
                )

    def test_api_surfaces_vector_search_failure_as_service_unavailable(self):
        request = OrchestratorRequest(profile={"state": "Tamil Nadu"})
        with patch(
            "api.index.run_orchestration_swarm",
            side_effect=tools.VectorSearchError("Gemini embeddings are unavailable."),
        ):
            with self.assertRaises(HTTPException) as raised:
                orchestrator_endpoint(request)

        self.assertEqual(raised.exception.status_code, 503)

    def test_gemini_can_reject_all_candidates_as_irrelevant(self):
        candidates = [{"id": "tn-business-loan"}]
        model = FakeChatModel('{"rankedSchemeIds":[]}')
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch.object(orchestrator, "_get_gemini_chat_model", return_value=model),
        ):
            ranked, status = orchestrator._rank_candidates_with_gemini(
                {"educationLevel": "GRADUATE", "occupation": "UNEMPLOYED"},
                candidates,
            )

        self.assertEqual(status, "NO_RELEVANT_CANDIDATES")
        self.assertEqual(ranked, [])


if __name__ == "__main__":
    unittest.main()
