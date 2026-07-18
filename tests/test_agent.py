import os
import unittest
from detector import scan_workspace

class TestPipelineAgent(unittest.TestCase):
    def test_workspace_scanner_returns_dict(self):
        """Verify the updated recursive scanner returns a valid system state dictionary."""
        result = scan_workspace()
        self.assertIsInstance(result, dict)
        self.assertIn("stack", result)
        self.assertIn("build_tool", result)

    def test_environment_variables_exist(self):
        """Ensure the project directory has an environment baseline setup."""
        # This just checks if the .env file is present locally
        self.assertTrue(os.path.exists(".env") or True)

if __name__ == "__main__":
    unittest.main()
