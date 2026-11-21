import asyncio
from io import BytesIO
import unittest

from fastapi import HTTPException
from starlette.datastructures import Headers, UploadFile

from api.index import document_ocr_endpoint


class DocumentUploadGuardrailTests(unittest.TestCase):
    def test_identity_documents_are_rejected_before_ocr(self):
        uploaded_file = UploadFile(
            filename="document.png",
            file=BytesIO(b"image-bytes"),
            headers=Headers({"content-type": "image/png"}),
        )

        with self.assertRaises(HTTPException) as raised:
            asyncio.run(document_ocr_endpoint(file=uploaded_file, category="identity"))

        self.assertEqual(raised.exception.status_code, 400)
        self.assertIn("Identity and bank documents", raised.exception.detail)

    def test_bank_documents_are_rejected_before_ocr(self):
        uploaded_file = UploadFile(
            filename="document.png",
            file=BytesIO(b"image-bytes"),
            headers=Headers({"content-type": "image/png"}),
        )

        with self.assertRaises(HTTPException) as raised:
            asyncio.run(document_ocr_endpoint(file=uploaded_file, category="bank"))

        self.assertEqual(raised.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
