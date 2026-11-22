import os
import subprocess
import sys
import unittest
from pathlib import Path


class VercelServiceImportTests(unittest.TestCase):
    def test_api_root_entrypoint_serves_health_and_intake(self):
        api_root = Path(__file__).resolve().parents[1]
        environment = os.environ.copy()
        environment["GEMINI_API_KEY"] = ""
        script = (
            "import index; "
            "assert index.health_check()['status'] == 'healthy'; "
            "result = index.intake_endpoint(index.IntakeRequest("
            "text='I completed B.Sc in 2024 and have been unemployed for 6 months.'"
            ")); "
            "assert result.extractionMode == 'HEURISTIC_FALLBACK'"
        )

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=api_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
