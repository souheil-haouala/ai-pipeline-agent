import os
import sys
from dotenv import load_dotenv
from google import genai
from detector import scan_workspace

def run_pipeline_agent():
    print("=" * 60)
    print("        AI AGENT: AUTOMATED PIPELINE INITIALIZER")
    print("=" * 60)
    
    # 1. Load and check environment credentials
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[ERROR] Missing GEMINI_API_KEY inside your .env file!")
        print("Please add your Google AI Studio token to proceed safely.")
        sys.exit(1)
        
    # 2. Run the dynamic workspace ecosystem detection
    try:
        scan_result = scan_workspace()
        stack = scan_result["stack"]
        build_tool = scan_result["build_tool"]
    except Exception as e:
        print(f"\n[ERROR] Workspace scanning failed: {e}")
        sys.exit(1)
        
    # Handle the unsupported/empty project fallback scenario gracefully
    if stack == "Generic":
        print("\n[WARNING] No recognizable project files (requirements.txt or package.json) found.")
        print("Aborting autonomous pipeline creation to prevent incorrect generation.")
        sys.exit(0)
        
    print(f"\n[SUCCESS] Targeted Environment Verified: {stack} ({build_tool})")
    print("Connecting to Google Gemini API cluster...")
    
    # 3. Securely connect and stream AI generation rules
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "You are an expert DevOps engineer. Provide ONLY the raw, valid YAML configuration content "
                f"for a GitHub Actions workflow (.github/workflows/main.yml) targeting a project built with {stack} "
                f"using {build_tool}. Do not wrap your response in markdown code blocks like ```yaml or include any chat text."
            ),
        )
        yaml_content = response.text.strip()
    except Exception as e:
        print(f"\n[ERROR] Cloud LLM communication failed: {e}")
        print("Please check your internet connection or API credit limits.")
        sys.exit(1)
        
    # 4. Handle structural file writing operations safely
    try:
        os.makedirs(".github/workflows", exist_ok=True)
        workflow_path = os.path.join(".github", "workflows", "main.yml")
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        
        print("\n" + "=" * 60)
        print(f"[SUCCESS] CI/CD Pipeline compiled and saved successfully!")
        print(f"Location: {workflow_path}")
        print("=" * 60)
        
    except IOError as e:
        print(f"\n[ERROR] Failed to write system files to disk: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline_agent()
