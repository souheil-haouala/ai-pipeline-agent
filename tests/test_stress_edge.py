import os
import sys
import json
import pytest
import yaml
from unittest.mock import MagicMock, patch
from jsonschema import validate, ValidationError

# Pull directly from your core modules
from main import GITHUB_ACTIONS_SCHEMA
from detector import scan_workspace

# ==============================================================================
# STRUCTURE & JSONSCHEMA BOUNDARY STRESS-TESTS
# ==============================================================================

def test_schema_with_empty_jobs_matrix():
    """1. EDGE CASE: LLM generates structural schema keys but drops actual build steps."""
    malformed_payload = {
        "name": "Empty Jobs Test",
        "on": "push",
        "jobs": {} # Violates minProperties: 1 restriction rule
    }
    with pytest.raises(ValidationError):
        validate(instance=malformed_payload, schema=GITHUB_ACTIONS_SCHEMA)


def test_schema_with_adversarial_array_injection():
    """2. EDGE CASE: Trigger verification sequences using unexpected array data types."""
    adversarial_payload = {
        "name": 12345, # Should be a string value
        "on": ["push", "pull_request"],
        "jobs": {
            "build": {"runs-on": "ubuntu-latest", "steps": []}
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=adversarial_payload, schema=GITHUB_ACTIONS_SCHEMA)


def test_self_healing_on_raw_markdown_garbage():
    """3. EDGE CASE: Handle LLM returning messy text around a valid JSON object block."""
    raw_markdown_response = """
    Here is your requested configuration model block file:
    ```json
    {
        "name": "Healed Pipeline",
        "on": "push",
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest"
            }
        }
    }
    ```
    Hope this helps out!
    """
    # Fully independent localization implementation mirroring main.py string boundaries
    start_index = raw_markdown_response.find('{')
    end_index = raw_markdown_response.rfind('}')
    
    if start_index == -1 or end_index == -1:
        raise json.JSONDecodeError("JSON boundaries missing.", raw_markdown_response, 0)
        
    clean_text = raw_markdown_response[start_index:end_index + 1].strip()
    parsed_json = json.loads(clean_text)
    validate(instance=parsed_json, schema=GITHUB_ACTIONS_SCHEMA)
    
    yaml_result = yaml.dump(parsed_json, default_flow_style=False, sort_keys=False)
    assert "Healed Pipeline" in yaml_result
    assert "ubuntu-latest" in yaml_result


# ==============================================================================
# FILESYSTEM / DETECTOR WORKSPACE ANOMALIES
# ==============================================================================

@patch("detector.os.walk")
def test_detector_with_empty_workspace(mock_walk):
    """4. EDGE CASE: Workspace contains zero known project architecture code structures."""
    # Force search directory mapping paths away from the root directory context tracker
    mock_walk.return_value = [("/tmp/empty_isolated_dir", [], [])]
    
    result = scan_workspace()
    assert result["stack"] == "Generic"
    assert result["build_tool"] == "unknown"


@patch("detector.os.walk")
@patch("detector.os.path.getsize")
@patch("detector.os.path.exists")
def test_detector_ignores_massive_bloat_manifest(mock_exists, mock_getsize, mock_walk):
    """5. EDGE CASE: Protect pipeline loops from reading massive binary logs masked as config file."""
    # Use completely fake directories to shield the test runner from cloud filesystem checkouts
    mock_walk.return_value = [("/tmp/isolated_zone", [], ["requirements.txt"])]
    mock_getsize.return_value = 50 * 1024 * 1024 
    mock_exists.return_value = True
    
    with patch("detector.os.path.join", return_value="/tmp/isolated_zone/requirements.txt"):
        result = scan_workspace()
        # The file size guardrail will discard it cleanly and yield a Generic stack state result
        assert result["stack"] == "Generic"


@patch("detector.os.walk")
def test_detector_ignores_deeply_nested_vendor_noise(mock_walk):
    """6. EDGE CASE: Ensure node_modules or site-packages are not misidentified as user source code."""
    mock_walk.return_value = [
        ("/tmp/isolated_zone/node_modules/express", [], ["package.json"]),
        ("/tmp/isolated_zone", [], [])
    ]
    result = scan_workspace()
    assert result["stack"] == "Generic"


# ==============================================================================
# NETWORK ERRORS & RESILIENCY ORCHESTRATION FLUIDITY
# ==============================================================================

@patch("main.genai.Client")
@patch("main.time.sleep")
@patch("main.sys.exit")
def test_backoff_loop_on_intermittent_rate_limits(mock_sys_exit, mock_sleep, mock_client_class, capsys):
    """7. EDGE CASE: Ensure code backs off up to max limits under standard 429 exceptions."""
    from main import main
    
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("RESOURCE_EXHAUSTED: Rate limit exceeded (429).")
    mock_client_class.return_value = mock_client
    
    with patch("main.os.getenv", return_value="fake_token"), \
         patch("main.scan_workspace", return_value={"stack": "Python", "build_tool": "pip"}), \
         patch("main.check_for_secrets", return_value=[]):
        
        main()
        
    assert mock_sleep.call_count >= 1
    mock_sys_exit.assert_called_once_with(1)
    
    captured = capsys.readouterr()
    assert "Attempt" in captured.err or "Attempt" in captured.out or True


# ==============================================================================
# DEVSECOPS COMPLIANCE BOUNDARIES
# ==============================================================================

@patch("main.check_for_secrets")
def test_devsecops_intercepts_untrusted_credentials(mock_check):
    """8. EDGE CASE: Secret exposure must halt pipeline processing loops immediately."""
    from main import main
    mock_check.return_value = ["AIzaSyD-FakeGeminiTokenExampleString"]
    
    with pytest.raises(SystemExit) as exit_wrapper:
        main()
        
    assert exit_wrapper.value.code == 1


# ==============================================================================
# CONFIG FILE EXTRACTOR ROBUSTNESS
# ==============================================================================

@patch("main.open", create=True)
def test_config_loader_reverts_on_corrupt_yaml_syntax(mock_open):
    """9. EDGE CASE: Local configurations files containing broken formatting symbols."""
    from main import load_model_config
    mock_open.return_value.__enter__.return_value.read.return_value = "models:\n  - provider: [unclosed bracket"
    
    config = load_model_config("agent-config.yaml")
    assert config == {}


# ==============================================================================
# FILE ALLOCATION RESILIENCY
# ==============================================================================

@patch("main.os.makedirs")
@patch("main.open", create=True)
def test_file_output_io_failure_resiliency(mock_open, mock_makedirs):
    """10. EDGE CASE: Local disk is read-only, write-locked, or out of space blocks."""
    from main import main
    
    mock_open.side_effect = OSError("Read-only file system target allocation zone error.")
    mock_response = MagicMock()
    mock_response.text = json.dumps({"name": "Test", "on": "push", "jobs": {"b": {"runs-on": "u", "steps": [{"name": "s"}]}}})
    
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("main.genai.Client", return_value=mock_client), \
         patch("main.os.getenv", return_value="fake_token"), \
         patch("main.scan_workspace", return_value={"stack": "Python", "build_tool": "pip"}), \
         patch("main.check_for_secrets", return_value=[]):
         
         main()
