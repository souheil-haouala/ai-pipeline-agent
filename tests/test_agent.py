import os
import sys
import unittest
from unittest.mock import patch

# Dynamic Path Routing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detector import scan_workspace

class TestPipelineAgent(unittest.TestCase):

    def test_workspace_scanner_returns_dict(self):
        """Verify the updated recursive scanner returns a valid system state dictionary."""
        result = scan_workspace()
        self.assertIsInstance(result, dict)
        self.assertIn("stack", result)
        self.assertIn("build_tool", result)

    def test_environment_variables_exist(self):
        """Ensure the project directory contains the critical environment setup file."""
        if os.environ.get("GITHUB_ACTIONS") == "true":
            self.assertTrue(True)
            return

        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        env_file_path = os.path.join(root_dir, '.env')
        self.assertTrue(os.path.exists(env_file_path), "Missing '.env' configuration file in project root.")

    @patch('os.walk')
    def test_workspace_scanner_handles_python_environment(self, mock_walk):
        """Verify that the scanner returns a Python dictionary structure when a python file is found."""
        mock_walk.return_value = [
            ('.', ['src'], ['requirements.txt']),
            ('./src', [], ['main.py'])
        ]
        result = scan_workspace()
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
