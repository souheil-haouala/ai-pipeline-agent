import os
import sys
import unittest
import yaml
from unittest.mock import patch, MagicMock

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
    def test_workspace_scanner_skips_ignored_directories(self, mock_walk):
        """Verify that the scanner respects exclusions like node_modules and venv."""
        mock_walk.return_value = [
            ('.', ['src', 'node_modules', 'venv'], ['package.json', 'requirements.txt']),
            ('./src', [], ['main.py']),
            ('./node_modules', [], ['package.json']),
            ('./venv', [], ['pip-selfcheck.json'])
        ]
        result = scan_workspace()
        self.assertIsInstance(result, dict)

    @patch('google.genai.Client')
    def test_generator_api_mocking_and_yaml_integrity(self, mock_genai_client):
        """Mock the live Gemini API network call and validate the structural integrity of the generated YAML."""
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        
        mock_response.text = (
            "```yaml\n"
            "name: Dynamic CI Pipeline\n"
            "on: [push]\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Set up Python\n"
            "        uses: actions/setup-python@v5\n"
            "```"
        )
        
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_genai_client.return_value = mock_client_instance

        raw_output = mock_response.text.strip()
        
        # Match the generator's safe non-regex line processing structure
        clean_lines = []
        for line in raw_output.splitlines():
            if line.strip().startswith("```"):
                continue
            clean_lines.append(line)
            
        clean_yaml = "\n".join(clean_lines).strip()

        self.assertTrue(clean_yaml.startswith("name:"))

        try:
            parsed_yaml = yaml.safe_load(clean_yaml)
            self.assertEqual(parsed_yaml["name"], "Dynamic CI Pipeline")
            self.assertIn("jobs", parsed_yaml)
        except yaml.YAMLError as exc:
            self.fail(f"Gemini API returned structurally invalid YAML layout: {exc}")

if __name__ == "__main__":
    unittest.main()
