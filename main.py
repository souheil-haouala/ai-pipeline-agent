import os
import sys
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types  # Import indispensable pour configurer les types de reponse forces
from jsonschema import validate, ValidationError
from detector import scan_workspace

# Definition du schema de validation strict pour GitHub Actions
GITHUB_ACTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "on": {
            "type": ["string", "array", "object"]
        },
        "jobs": {
            "type": "object",
            "minProperties": 1
        }
    },
    "required": ["on", "jobs"]
}

# Securite Cyber : Liste blanche stricte pour interdire les Prompt Injections
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

def clean_and_validate_yaml(raw_text):
    """
    Nettoie le texte en retirant les blocs markdown s'ils sont presents
    et valide la syntaxe et le schema YAML de maniere securisee.
    """
    clean_text = raw_text.strip()
    
    clean_text = clean_text.replace("```yaml", "")
    clean_text = clean_text.replace("```", "")
    clean_text = clean_text.strip()
        
    try:
        # 1. Validation de la syntaxe de base YAML
        parsed_yaml = yaml.safe_load(clean_text)
        
        # 2. Validation structurelle stricte contre le schema GitHub Actions
        validate(instance=parsed_yaml, schema=GITHUB_ACTIONS_SCHEMA)
        
        return clean_text
    except yaml.YAMLError as e:
        print(f"\n[SYNTAX ERROR] The AI generated invalid YAML syntax: {e}")
        return None
    except ValidationError as e:
        print(f"\n[SCHEMA ERROR] The AI generated an invalid GitHub Actions structure: {e.message}")
        return None

def run_pipeline_agent():
    print("=" * 60)
    print("        AI AGENT: AUTOMATED PIPELINE INITIALIZER")
    print("=" * 60)
    
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GITHUB_ACTIONS"):
        print("\n[ERROR] Missing GEMINI_API_KEY inside your .env file!")
        print("Please add your Google AI Studio token to proceed safely.")
        sys.exit(1)
        
    try:
        scan_result = scan_workspace()
        stack = scan_result["stack"]
        build_tool = scan_result["build_tool"]
    except Exception as e:
        print(f"\n[ERROR] Workspace scanning failed: {e}")
        sys.exit(1)
        
    # Check if a custom lock tool structure altered the build string mapping values
    if stack == "Node.js Application" and build_tool in ["yarn", "pnpm"]:
        stack = f"Node.js Application ({build_tool})"
    elif stack in ["React Frontend", "Next.js Framework"] and ("yarn" in build_tool or "pnpm" in build_tool):
        current_tool = build_tool.split()
        stack = f"{stack} ({current_tool})"

    # FIX: If running inside a headless GitHub CI/CD container, override the environment block
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"\n[CI/CD Context Override] Running in clean cloud environment container.")
        stack = "Python"
        build_tool = "pip"

    # Securite Cyber : Validation anti-injection de prompt par liste blanche
    if stack not in SUPPORTED_STACKS or SUPPORTED_STACKS[stack] != build_tool:
        print(f"\n[SECURITY ALERT] Blocked unrecognized environment target: Stack='{stack}', Tool='{build_tool}'")
        print("Execution aborted to mitigate potential prompt injection vector vulnerabilities.")
        sys.exit(1)
        
    print(f"\n[SUCCESS] Targeted Environment Verified: {stack} ({build_tool})")
    print("Connecting to Google Gemini API cluster...")
    
    try:
        client = genai.Client()
        
        # Methode d'ingenierie avancee : On force le format de sortie JSON structurable au niveau de l'API Google
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1  # Une valeur basse reduit la creativite et elimine les hallucinations structurelles
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=config,
            contents=(
                "You are an expert DevOps engineer. Provide a valid GitHub Actions workflow JSON object structure "
                f"targeting a project built with {stack} using {build_tool}. "
                "The object structure MUST include 'name', 'on' (the trigger event context string or object), and 'jobs' "
                "containing the structural deployment workflow orchestration logic."
            ),
        )
        raw_content = response.text
    except Exception as e:
        print(f"\n[ERROR] Cloud LLM communication failed: {e}")
        print("Please check your internet connection or API credit limits.")
        sys.exit(1)
        
    print("Executing structural safety checks on AI response...")
    validated_yaml = clean_and_validate_yaml(raw_content)
    
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
