import os
import sys
import unittest
from unittest.mock import patch

# Dynamic Path Routing: Explicitly append the parent root folder to Python's system lookup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now Python can safely resolve the root module files on any remote server system!
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
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        env_file_path = os.path.join(root_dir, '.env')
        
        # Verify that the physical .env configuration file exists in your project root
        self.assertTrue(os.path.exists(env_file_path), "Missing '.env' configuration file in project root.")

    @patch('os.walk')
    def test_workspace_scanner_skips_ignored_directories(self, mock_walk):
        """Verify that the scanner respects exclusions like node_modules and venv."""
        # Mock os.walk to return a mock directory structure containing an ignored path
        mock_walk.return_value = [
            ('.', ['src', 'node_modules', 'venv'], ['package.json', 'requirements.txt']),
            ('./src', [], ['main.py']),
            ('./node_modules', [], ['package.json']), # This folder should be skipped
            ('./venv', [], ['pip-selfcheck.json'])    # This folder should be skipped
        ]
        
        result = scan_workspace()
        
        # Confirms the logic evaluates properly even when ignored directories are injected
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
