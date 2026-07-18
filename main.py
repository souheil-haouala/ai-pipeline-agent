import os
import sys
import yaml
import time
from colorama import init, Fore, Style
from dotenv import load_dotenv
from google import genai
from google.genai import types  
from jsonschema import validate, ValidationError
from detector import scan_workspace

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

def validate_and_convert_to_yaml(raw_json_text):
    """Validates structural AI JSON output and converts it cleanly to standard YAML."""
    try:
        parsed_data = yaml.safe_load(raw_json_text)
        validate(instance=parsed_data, schema=GITHUB_ACTIONS_SCHEMA)
        clean_yaml = yaml.dump(parsed_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return clean_yaml
    except (yaml.YAMLError, ValueError, TypeError) as e:
        print_error(f"The AI generated invalid JSON/YAML structure: {e}")
        return None
    except ValidationError as e:
        print_error(f"Invalid GitHub Actions structure: {e.message}")
        return None

def run_pipeline_agent():
    print_header()
    start_time = time.time()
    
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GITHUB_ACTIONS"):
        print_error("Missing GEMINI_API_KEY inside your .env configuration schema file!")
        sys.exit(1)
        
    print_step("Analyzing workspace tree layer depth values recursively")
    try:
        scan_result = scan_workspace()
        stack = scan_result["stack"]
        build_tool = scan_result["build_tool"]
    except Exception as e:
        print_error(f"Workspace directory parsing sweep failed: {e}")
        sys.exit(1)
        
    if stack == "Node.js Application" and build_tool in ["yarn", "pnpm"]:
        stack = f"Node.js Application ({build_tool})"
    elif stack in ["React Frontend", "Next.js Framework"] and ("yarn" in build_tool or "pnpm" in build_tool):
        tool_name = build_tool.split()
        stack = f"{stack} ({tool_name})"

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"\n{Fore.YELLOW}[i] Cloud Container Override Action: Mapping validation matrix constraints.")
        stack = "Python"
        build_tool = "pip"

    if stack not in SUPPORTED_STACKS or SUPPORTED_STACKS[stack] != build_tool:
        print_error(f"Security Blocker Intercepted: Stack='{stack}', Tool='{build_tool}'")
        sys.exit(1)
        
    print_success(f"Ecosystem Verified: {stack} via {build_tool}")
    
    max_retries = 3
    retry_delay = 5  # Initial cooldown delay in seconds
    raw_content = None
    
    for attempt in range(1, max_retries + 1):
        print_step(f"Opening handshake socket connection to Google Gemini API cluster (Attempt {attempt}/{max_retries})")
        try:
            client = genai.Client()
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
            
            prompt = (
                "You are an expert DevOps engineer. Provide a valid GitHub Actions workflow schema formatted as a JSON object "
                f"targeting a project built with {stack} using '{build_tool}'. "
                "The JSON object MUST strictly use standard GitHub actions keys like 'name', 'on', and 'jobs'. "
                "Ensure the jobs contain operational verification steps matching this ecosystem."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=config,
                contents=prompt,
            )
            raw_content = response.text
            break  # Break out of the loop if successful!
            
        except Exception as e:
            error_str = str(e)
            # COOLDOWN PATCH: Handles both 429 quota exhaustion and 503 server overloads smoothly
            if any(marker in error_str for marker in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                if attempt < max_retries:
                    print_warning(f"Network congestion or rate limit hit. Initiating automatic cooldown backoff...")
                    # Stylized visual countdown loop in the console
                    for remaining in range(retry_delay, 0, -1):
                        sys.stdout.write(f"\r{Fore.YELLOW}[!] Retrying network operation in {remaining}s... ")
                        sys.stdout.flush()
                        time.sleep(1)
                    print()  # Shift to a clean line break
                    retry_delay *= 2  # Exponential backoff multiplier
                    continue
                else:
                    print_error(f"API server thresholds or limitations reached after max retries: {e}")
                    sys.exit(1)
            else:
                print_error(f"Cloud server socket connection dropped: {e}")
                sys.exit(1)
                
    if not raw_content:
        print_error("Process terminated: Failed to collect execution parameters from the LLM.")
        sys.exit(1)
        
    print_step("Executing schema conformance audit and structural formatting validation")
    validated_yaml = validate_and_convert_to_yaml(raw_content)
    
    if not validated_yaml:
        print_error("Process terminated: Output workflow layout configuration is corrupted.")
        sys.exit(1)
        
    try:
        os.makedirs(os.path.join(".github", "workflows"), exist_ok=True)
        workflow_path = os.path.join(".github", "workflows", "main.yml")
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(validated_yaml)
        
        elapsed_time = time.time() - start_time
        print(Fore.CYAN + "=" * 65)
        print_success(f"CI/CD Pipeline compiled and saved successfully in {elapsed_time:.2f}s!")
        print(f"{Fore.WHITE}Destination Path: {Fore.YELLOW}{workflow_path}")
        print(Fore.CYAN + "=" * 65)
        
    except IOError as e:
        print_error(f"Failed to record asset payload stream to disk: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline_agent()
