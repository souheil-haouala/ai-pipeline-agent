import os
import sys
import yaml
import json
import time
from colorama import init, Fore, Style
from dotenv import load_dotenv
from google import genai
from google.genai import types  
from jsonschema import validate, ValidationError
from detector import scan_workspace, check_for_secrets

# Initialize colorama for cross-platform color rendering
init(autoreset=True)

GITHUB_ACTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "on": {"type": ["string", "array", "object"]},
        "jobs": {
            "type": "object",
            "minProperties": 1
        }
    },
    "required": ["on", "jobs"]
}

SUPPORTED_STACKS = {
    "Python": "pip",
    "Python (Scripting)": "python",
    "Node.js": "npm",
    "Node.js Application": "npm",
    "Node.js Application (yarn)": "yarn",
    "Node.js Application (pnpm)": "pnpm",
    "React Frontend": "npm run build",
    "React Frontend (yarn)": "yarn run build",
    "React Frontend (pnpm)": "pnpm run build",
    "Next.js Framework": "npm run build",
    "Next.js Framework (yarn)": "yarn run build",
    "Next.js Framework (pnpm)": "pnpm run build",
    "Vue Frontend": "npm run build",
    "Angular Frontend": "npm run build",
    "Nuxt Framework": "npm run build",
    "Docker Containerization": "docker",
    "Go": "go build",
    "Java": "maven",
    "Java/Kotlin": "gradle"
}

DEFAULT_MODEL_NAME = "gemini-2.5-flash"


def load_model_config(config_path=None):
    """Load model configuration from a YAML file if one is available."""
    candidates = []
    if config_path:
        candidates.append(config_path)

    env_path = os.environ.get("MODEL_CONFIG_PATH")
    if env_path:
        candidates.append(env_path)

    candidates.extend([
        "agent-config.yaml",
        "models.yaml",
        ".ai-pipeline-agent.yaml",
        os.path.join(".github", "models.yaml"),
    ])

    seen_paths = set()
    for candidate in candidates:
        if not candidate or candidate in seen_paths:
            continue
        seen_paths.add(candidate)

        if not os.path.exists(candidate):
            continue

        try:
            with open(candidate, "r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            if isinstance(data, dict):
                return data
        except (OSError, yaml.YAMLError) as exc:
            print_warning(f"Unable to load model config from {candidate}: {exc}")

    return {}


def resolve_generation_model(model_config):
    """Select the preferred Gemini model from the loaded configuration."""
    if not isinstance(model_config, dict):
        return None

    tab_model = model_config.get("tabAutocompleteModel")
    if isinstance(tab_model, dict) and tab_model.get("provider") == "gemini":
        return tab_model

    models = model_config.get("models", [])
    if isinstance(models, list):
        for entry in models:
            if isinstance(entry, dict) and entry.get("provider") == "gemini":
                return entry

    return None


def print_header():
    """Renders a stylized corporate terminal panel header block."""
    print(Fore.CYAN + Style.BRIGHT + "=" * 65)
    print(Fore.CYAN + Style.BRIGHT + "   🤖  AI PIPELINE AGENT : AUTONOMOUS ORCHESTRATION ENGINE")
    print(Fore.CYAN + Style.BRIGHT + "=" * 65)

def print_step(message):
    print(f"{Fore.BLUE}[{Fore.WHITE}* {Fore.BLUE}]{Fore.WHITE} {message}...")

def print_success(message):
    print(f"{Fore.GREEN}[{Fore.WHITE}✓{Fore.GREEN}] {Fore.GREEN}{Style.BRIGHT}{message}")

def print_error(message):
    print(f"{Fore.RED}[{Fore.WHITE}✗{Fore.RED}] {Fore.RED}{Style.BRIGHT}{message}", file=sys.stderr)

def print_warning(message):
    print(f"{Fore.YELLOW}[{Fore.WHITE}!{Fore.YELLOW}] {Fore.YELLOW}{Style.BRIGHT}{message}")


def validate_and_convert_to_yaml(raw_json_text, client=None, model_name=DEFAULT_MODEL_NAME):
    """Validates structural AI JSON output and converts it cleanly to standard YAML with Self-Healing."""
    try:
        clean_text = raw_json_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        parsed_json = json.loads(clean_text)
        validate(instance=parsed_json, schema=GITHUB_ACTIONS_SCHEMA)
        
        yaml_output = yaml.dump(parsed_json, default_flow_style=False, sort_keys=False)
        return yaml_output

    except (json.JSONDecodeError, ValidationError) as e:
        print_warning(f"Validation failed: {str(e)}")
        if client:
            print_step("Self-Healing Activated! Asking Gemini to fix the configuration structure")
            healing_prompt = f"""
            The previous output failed validation with the following error: {str(e)}
            Here is the invalid payload:
            {raw_json_text}
            
            Please fix the payload. Return ONLY a strictly compliant JSON object matching the GitHub Actions schema. No markdown wrapping.
            """
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=healing_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                return validate_and_convert_to_yaml(response.text, client=None)
            except Exception as healing_error:
                print_error(f"Self-healing structural recovery failed: {healing_error}")
                raise healing_error
        else:
            raise e


def main():
    load_dotenv()
    print_header()
    
    # --- PROACTIVE DEVSECOPS SECURITY SCAN ---
    print_step("Running proactive DevSecOps static security audit")
    detected_secrets = check_for_secrets()
    if detected_secrets:
        print_error("Security Breach Detected! Hardcoded tokens found in codebase:")
        for secret in detected_secrets:
            print(f"  -> {Fore.YELLOW}{secret}")
        print_error("Orchestration lifecycle aborted to prevent remote token leakage.")
        sys.exit(1)
    else:
        print_success("Security Audit Passed: No hardcoded secret tokens leaked in workspace")
    # ------------------------------------------
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("Missing GEMINI_API_KEY in environment or .env file.")
        sys.exit(1)
        
    config = load_model_config()
    model_entry = resolve_generation_model(config)
    model_name = model_entry.get("model", DEFAULT_MODEL_NAME) if model_entry else DEFAULT_MODEL_NAME
    
    print_step("Analyzing workspace tree layer depth values recursively")
    ecosystem = scan_workspace()
    
    stack_name = ecosystem.get("stack", "Generic")
    build_tool = ecosystem.get("build_tool", "unknown")
    
    if stack_name not in SUPPORTED_STACKS:
        print_warning(f"Detected stack '{stack_name}' is not in security allowlist. Proceeding with caution.")
    else:
        print_success(f"Ecosystem Verified: {stack_name} via {build_tool}")
        
    print_step(f"Opening handshake socket connection to Google Gemini API ({model_name})")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Generate a complete, enterprise-grade production-ready GitHub Actions workflow for a {stack_name} application using {build_tool}.
    Include steps for checking out code, setting up environments, installing dependencies, running tests, and basic build actions.
    Return the response strictly inside a structural JSON object that matches the GitHub Actions metadata syntax format.
    """
    
    attempts = 3
    raw_response_text = ""
    for attempt in range(1, attempts + 1):
        try:
            print_step(f"Executing schema conformance audit and generation (Attempt {attempt}/{attempts})")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw_response_text = response.text
            break  # Sortie de la boucle en cas de succès
        except Exception as err:
            if "429" in str(err) or "RESOURCE_EXHAUSTED" in str(err):
                print_warning(f"Rate limit reached (429). Waiting 15 seconds before retry...")
                time.sleep(15)
            else:
                print_error(f"Network request failed: {err}")
                if attempt == attempts:
                    sys.exit(1)
                    
    if not raw_response_text:
        print_error("Failed to collect any payload back from the Gemini cluster.")
        sys.exit(1)
        
    print_step("Validating layout structure and converting to standard deployment YAML")
    try:
        final_yaml = validate_and_convert_to_yaml(raw_response_text, client=client, model_name=model_name)
        print_success("Workflow configuration successfully generated, validated and healed!")
        print("\n" + Fore.WHITE + final_yaml)
    except Exception as validation_failure:
        print_error(f"Execution pipeline interrupted due to unrecoverable structure: {validation_failure}")
        sys.exit(1)


if __name__ == "__main__":
    main()
