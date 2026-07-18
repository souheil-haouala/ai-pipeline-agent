import os
import sys
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types  
from jsonschema import validate, ValidationError
from detector import scan_workspace

# Définition d'un schéma de validation plus robuste
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

def validate_and_convert_to_yaml(raw_json_text):
    """
    Valide le JSON de l'IA par rapport au schéma structurel, 
    puis le convertit en une chaîne YAML propre.
    """
    try:
        # 1. Chargement sécurisé du JSON natif renvoyé par Gemini
        parsed_data = yaml.safe_load(raw_json_text)
        
        # 2. Validation structurelle stricte
        validate(instance=parsed_data, schema=GITHUB_ACTIONS_SCHEMA)
        
        # 3. Conversion propre en format YAML standard
        clean_yaml = yaml.dump(parsed_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return clean_yaml
    except (yaml.YAMLError, ValueError, TypeError) as e:
        print(f"\n[SYNTAX ERROR] The AI generated invalid JSON/YAML structure: {e}")
        return None
    except ValidationError as e:
        print(f"\n[SCHEMA ERROR] Invalid GitHub Actions structure: {e.message}")
        return None

def run_pipeline_agent():
    print("=" * 60)
    print("        AI AGENT: AUTOMATED PIPELINE INITIALIZER")
    print("=" * 60)
    
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GITHUB_ACTIONS"):
        print("\n[ERROR] Missing GEMINI_API_KEY inside your .env file!")
        sys.exit(1)
        
    try:
        scan_result = scan_workspace()
        stack = scan_result["stack"]
        build_tool = scan_result["build_tool"]
    except Exception as e:
        print(f"\n[ERROR] Workspace scanning failed: {e}")
        sys.exit(1)
        
    # CORRECTION : Align target mapping modifications without dropping build string syntax dependencies
    if stack == "Node.js Application" and build_tool in ["yarn", "pnpm"]:
        stack = f"Node.js Application ({build_tool})"
    elif stack in ["React Frontend", "Next.js Framework"] and ("yarn" in build_tool or "pnpm" in build_tool):
        tool_name = build_tool.split()[0]
        stack = f"{stack} ({tool_name})"

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"\n[CI/CD Context Override] Running in clean cloud environment container.")
        stack = "Python"
        build_tool = "pip"

    if stack not in SUPPORTED_STACKS or SUPPORTED_STACKS[stack] != build_tool:
        print(f"\n[SECURITY ALERT] Blocked unrecognized environment target: Stack='{stack}', Tool='{build_tool}'")
        sys.exit(1)
        
    print(f"\n[SUCCESS] Targeted Environment Verified: {stack} ({build_tool})")
    print("Connecting to Google Gemini API cluster...")
    
    try:
        client = genai.Client()
        
        # Configuration pass matching the official google-genai structural schema rules
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
        
        prompt = (
            "You are an expert DevOps engineer. Provide a valid GitHub Actions workflow schema formatted as a JSON object "
            f"targeting a project built with {stack} using '{build_tool}'. "
            "The JSON object MUST strictly use standard GitHub actions keys like 'name', 'on', and 'jobs'. "
            "Ensure the jobs contain operational verification steps (e.g. linter, tests, or build steps) matching this ecosystem."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=config,
            contents=prompt,
        )
        raw_content = response.text
    except Exception as e:
        print(f"\n[ERROR] Cloud LLM communication failed: {e}")
        sys.exit(1)
        
    print("Executing structural safety and format conversion checks...")
    validated_yaml = validate_and_convert_to_yaml(raw_content)
    
    if not validated_yaml:
        print("[CRITICAL] Process aborted: Output pipeline blueprint is structurally unstable.")
        sys.exit(1)
        
    try:
        os.makedirs(os.path.join(".github", "workflows"), exist_ok=True)
        workflow_path = os.path.join(".github", "workflows", "main.yml")
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(validated_yaml)
        
        print("\n" + "=" * 60)
        print(f"[SUCCESS] CI/CD Pipeline compiled and saved successfully!")
        print(f"Location: {workflow_path}")
        print("=" * 60)
        
    except IOError as e:
        print(f"\n[ERROR] Failed to write system files to disk: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline_agent()
