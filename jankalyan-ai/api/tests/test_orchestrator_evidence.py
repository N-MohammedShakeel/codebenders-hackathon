import unittest
from unittest.mock import patch

from api.index import orchestrator_endpoint
from api.models import DocumentEvidence, OrchestratorRequest
from api.agent.orchestrator import run_orchestration_swarm
from api.agent.tools import load_schemes_catalog, get_official_search_domains


class OrchestratorDocumentEvidenceTests(unittest.TestCase):
    def test_official_search_domains_cover_more_state_websites(self):
        expected_domains = {
            "Andhra Pradesh": ["sspensions.ap.gov.in", "jnanabhumi.ap.gov.in"],
            "Karnataka": ["sevasindhuservices.karnataka.gov.in", "ssp.postmatric.karnataka.gov.in"],
            "Kerala": ["egrantz.kerala.gov.in", "sjd.kerala.gov.in"],
            "Tamil Nadu": ["tnsocialwelfare.tn.gov.in", "tnhealth.tn.gov.in"],
            "Telangana": ["telanganaepass.cgg.gov.in", "rythubandhu.telangana.gov.in"],
        }
        for state, required_domains in expected_domains.items():
            domains = get_official_search_domains(state)
            self.assertTrue(all(domain in domains for domain in required_domains), state)

        central_domains = get_official_search_domains("All India")
        self.assertIn("india.gov.in", central_domains)
        self.assertIn("scholarships.gov.in", central_domains)

    def test_only_current_income_evidence_overrides_profile_income(self):
        request = OrchestratorRequest(
            profile={"state": "Tamil Nadu", "familyAnnualIncome": 120000},
            documentEvidence=[
                {
                    "documentId": "old-income",
                    "category": "income",
                    "validityStatus": "EXPIRED",
                    "extracted": {"annualIncomeINR": 40000},
                    "savedAt": "2026-01-01T00:00:00Z",
                },
                {
                    "documentId": "current-income",
                    "category": "income",
                    "validityStatus": "CURRENT",
                    "extracted": {"annualIncomeINR": 80000},
                    "savedAt": "2026-02-01T00:00:00Z",
                },
            ],
        )

        with patch("api.index.run_orchestration_swarm", return_value=([], [], [])) as run_swarm:
            orchestrator_endpoint(request)

        self.assertEqual(run_swarm.call_args.args[0]["familyAnnualIncome"], 80000)
        self.assertNotIn("landHoldingAcres", run_swarm.call_args.args[0])
        self.assertEqual(len(run_swarm.call_args.args[1]), 2)

    def test_unconfirmed_income_evidence_does_not_override_profile(self):
        request = OrchestratorRequest(
            profile={"state": "Tamil Nadu", "familyAnnualIncome": 120000},
            documentEvidence=[
                DocumentEvidence(
                    documentId="review-income",
                    category="income",
                    validityStatus="REVIEW_REQUIRED",
                    extracted={"annualIncomeINR": 50000},
                    savedAt="2026-02-01T00:00:00Z",
                )
            ],
        )

        with patch("api.index.run_orchestration_swarm", return_value=([], [], [])) as run_swarm:
            orchestrator_endpoint(request)

        self.assertEqual(run_swarm.call_args.args[0]["familyAnnualIncome"], 120000)

    def test_selected_state_filters_candidates_and_uses_official_search(self):
        profile = {
            "state": "Tamil Nadu",
            "educationLevel": "GRADUATE",
            "occupation": "UNEMPLOYED",
            "familyAnnualIncome": 120000,
        }
        with patch(
            "api.agent.orchestrator.search_in_memory_schemes",
            return_value=[
                scheme for scheme in load_schemes_catalog()
                if scheme["state"] == "Tamil Nadu"
            ][:12],
        ), patch(
            "api.agent.orchestrator._rank_candidates_with_gemini",
            side_effect=lambda _profile, schemes: (schemes, "RERANKED"),
        ), patch(
            "api.agent.orchestrator.live_tavily_search",
            return_value={"results": [], "isMock": True, "verifiedAt": "test"},
        ) as live_search:
            matches, near_misses, trace = run_orchestration_swarm(profile)

        self.assertEqual(matches, [])
        self.assertEqual(near_misses, [])
        self.assertTrue(trace[1].output["candidateIds"])
        manual_ids = set(trace[1].output["manualReviewCandidateIds"])
        self.assertTrue(manual_ids)
        self.assertLessEqual(len(manual_ids), 8)
        self.assertTrue(all(not scheme_id.startswith("ka-") for scheme_id in manual_ids))
        self.assertTrue(all(not scheme_id.startswith("ka-") for scheme_id in trace[1].output["candidateIds"]))
        live_search.assert_called_once()
        self.assertEqual(live_search.call_args.kwargs["state"], "Tamil Nadu")

    def test_expanded_catalog_covers_requested_states_and_manual_records_are_returned(self):
        catalog = load_schemes_catalog()
        requested_states = {"Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Telangana"}

        self.assertTrue(requested_states.issubset({scheme["state"] for scheme in catalog}))
        manual_records = [scheme for scheme in catalog if scheme.get("eligibilityMode") == "MANUAL_REVIEW"]
        self.assertTrue(manual_records)
        self.assertTrue(all(scheme["officialPortalUrl"].startswith("https://") for scheme in manual_records))

        request = OrchestratorRequest(
            profile={"state": "Tamil Nadu", "educationLevel": "GRADUATE", "occupation": "UNEMPLOYED"},
        )
        with patch(
            "api.agent.orchestrator.search_in_memory_schemes",
            return_value=[
                scheme for scheme in catalog
                if scheme["state"] in {"Tamil Nadu", "All India"}
            ][:12],
        ), patch(
            "api.agent.orchestrator._rank_candidates_with_gemini",
            side_effect=lambda _profile, schemes: (schemes, "RERANKED"),
        ), patch(
            "api.agent.orchestrator.live_tavily_search",
            return_value={"results": [], "isMock": True, "verifiedAt": "test"},
        ):
            response = orchestrator_endpoint(request)

        self.assertTrue(response.manualReviewSchemes)
        self.assertTrue(all(
            scheme.state in {"Tamil Nadu", "All India"}
            for scheme in response.manualReviewSchemes
        ))
        self.assertTrue(all(scheme.eligibilityMode == "MANUAL_REVIEW" for scheme in response.manualReviewSchemes))

    def test_catalog_has_broad_sector_coverage_and_source_metadata(self):
        catalog = load_schemes_catalog()
        self.assertGreaterEqual(len(catalog), 100)

        manual_records = [scheme for scheme in catalog if scheme.get("eligibilityMode") == "MANUAL_REVIEW"]
        self.assertGreaterEqual(len(manual_records), 90)

        sectors = {scheme["category"] for scheme in catalog}
        self.assertTrue({"EDUCATION", "HEALTH", "AGRICULTURE", "HOUSING", "EMPLOYMENT"}.issubset(sectors))

        for scheme in manual_records:
            criteria = scheme.get("eligibilityCriteria", [])
            sources = scheme.get("sourceUrls", [])
            self.assertTrue(criteria, scheme["id"])
            self.assertTrue(sources, scheme["id"])
            self.assertTrue(all(url.startswith("https://") for url in sources), scheme["id"])


if __name__ == "__main__":
    unittest.main()
