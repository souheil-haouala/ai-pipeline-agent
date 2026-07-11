import os
import sys
import yaml
from dotenv import load_dotenv
from google import genai
from detector import scan_workspace

def clean_and_validate_yaml(raw_text):
    """
    Nettoie le texte en retirant les blocs markdown s'ils sont presents
    et valide la syntaxe YAML de maniere securisee.
    """
    clean_text = raw_text.strip()
    
    # Methode Senior : On retire proprement les balises markdown
    clean_text = clean_text.replace("```yaml", "")
    clean_text = clean_text.replace("```", "")
    clean_text = clean_text.strip()
        
    try:
        yaml.safe_load(clean_text)
        return clean_text
    except yaml.YAMLError as e:
        print(f"\n[VALIDATION ERROR] The AI generated invalid YAML syntax: {e}")
        return None

def run_pipeline_agent():
    print("=" * 60)
    print("        AI AGENT: AUTOMATED PIPELINE INITIALIZER")
    print("=" * 60)
    
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
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
        
    if stack == "Generic":
        print("\n[WARNING] No recognizable project architecture layout found.")
        print("Aborting autonomous pipeline creation to prevent incorrect generation.")
        sys.exit(0)
        
    print(f"\n[SUCCESS] Targeted Environment Verified: {stack} ({build_tool})")
    print("Connecting to Google Gemini API cluster...")
    
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Bascule sur le moteur de secours pour eviter la limite 429
            contents=(
                "You are an expert DevOps engineer. Provide ONLY the raw, valid YAML configuration content "
                f"for a GitHub Actions workflow (.github/workflows/main.yml) targeting a project built with {stack} "
                f"using {build_tool}. Do not wrap your response in markdown code blocks like ```yaml or include any chat text."
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
    