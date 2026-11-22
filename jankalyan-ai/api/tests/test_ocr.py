import datetime
import os
import unittest
from unittest.mock import patch
from google.api_core.exceptions import ResourceExhausted

from api.agent.ocr import analyze_document_image, OCRServiceError, _provider_error_message


class DocumentOCRAssessmentTests(unittest.TestCase):
    def analyze(self, values, category="income"):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch("api.agent.ocr._call_vision_ai", return_value=values):
                return analyze_document_image(b"image", "private-name.png", "image/png", category)

    def test_explicit_future_expiry_is_current(self):
        expiry = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        result = self.analyze({"documentCategory": "income", "expiryDate": expiry})

        self.assertEqual(result["validity"]["status"], "CURRENT")
        self.assertEqual(result["extracted"]["expiryDate"], expiry)

    def test_expired_document_is_not_current(self):
        expiry = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        result = self.analyze({"documentCategory": "income", "expiryDate": expiry})

        self.assertEqual(result["validity"]["status"], "EXPIRED")

    def test_missing_expiry_requires_manual_review(self):
        result = self.analyze({"documentCategory": "income", "issueDate": "2024-01-01"})

        self.assertEqual(result["validity"]["status"], "REVIEW_REQUIRED")

    def test_mismatched_category_requires_review(self):
        result = self.analyze({"documentCategory": "education", "expiryDate": "2099-12-31"})

        self.assertEqual(result["validity"]["status"], "TYPE_MISMATCH")

    def test_future_issue_date_requires_review(self):
        issue_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        result = self.analyze({
            "documentCategory": "income",
            "issueDate": issue_date,
            "expiryDate": "2099-12-31",
        })

        self.assertEqual(result["validity"]["status"], "REVIEW_REQUIRED")

    def test_unrecognized_document_type_is_not_persisted(self):
        result = self.analyze({
            "documentCategory": "income",
            "documentType": "Income Certificate for Jane Doe",
            "expiryDate": "2099-12-31",
        })

        self.assertIsNone(result["extracted"]["documentType"])
        self.assertEqual(result["fileName"], "document")

    def test_resource_exhausted_returns_quota_guidance(self):
        message = _provider_error_message(ResourceExhausted("429 quota exceeded"))

        self.assertIn("quota", message.lower())
        self.assertIn("billing", message.lower())


if __name__ == "__main__":
    unittest.main()
