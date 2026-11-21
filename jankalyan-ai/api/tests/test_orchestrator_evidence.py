import unittest
from unittest.mock import patch

from api.index import orchestrator_endpoint
from api.models import DocumentEvidence, OrchestratorRequest
from api.agent.orchestrator import run_orchestration_swarm
from api.agent.tools import load_schemes_catalog


class OrchestratorDocumentEvidenceTests(unittest.TestCase):
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
            "api.agent.orchestrator.live_tavily_search",
            return_value={"results": [], "isMock": True, "verifiedAt": "test"},
        ) as live_search:
            matches, near_misses, trace = run_orchestration_swarm(profile)

        self.assertEqual(matches, [])
        self.assertEqual(near_misses, [])
        self.assertTrue(trace[1].output["candidateIds"])
        self.assertEqual(
            trace[1].output["manualReviewCandidateIds"],
            [scheme_id for scheme_id in trace[1].output["candidateIds"]],
        )
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
            "api.agent.orchestrator.live_tavily_search",
            return_value={"results": [], "isMock": True, "verifiedAt": "test"},
        ):
            response = orchestrator_endpoint(request)

        self.assertTrue(response.manualReviewSchemes)
        self.assertTrue(all(scheme.state == "Tamil Nadu" for scheme in response.manualReviewSchemes))
        self.assertTrue(all(scheme.eligibilityMode == "MANUAL_REVIEW" for scheme in response.manualReviewSchemes))


if __name__ == "__main__":
    unittest.main()
