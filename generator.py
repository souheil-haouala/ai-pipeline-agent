import os
from dotenv import load_dotenv
from google import genai
from detector import scan_workspace

# Load credentials
load_dotenv()

# Initialize the Gemini Client explicitly pulling the key from os.environ
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Dynamically trigger the live workspace scan!
scan_result = scan_workspace()
detected_stack = scan_result["stack"]
build_tool = scan_result["build_tool"]

print(f"\nDetected Target Environment: {detected_stack} ({build_tool})")
print("Contacting Google Gemini to generate your autonomous CI pipeline...")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "You are an expert DevOps engineer. Provide the valid YAML configuration content "
            f"for a GitHub Actions workflow (.github/workflows/main.yml) targeting a project built with {detected_stack} "
            f"using {build_tool}. Provide only the configuration content itself."
        ),
    )

    raw_output = response.text.strip()
    
    # Structural Clean: Strip out backtick lines completely without regex bugs
    clean_lines = []
    for line in raw_output.splitlines():
        if line.strip().startswith("```"):
            continue
        clean_lines.append(line)
        
    clean_yaml = "\n".join(clean_lines).strip()

    # Write the dynamic asset configuration directly to disk
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/main.yml", "w", encoding="utf-8") as f:
        f.write(clean_yaml)
    
    print("\nSuccess! Infrastructure pipeline generated dynamically based on active code parameters.")

except Exception as e:
    print(f"\nAn error occurred during generation: {e}")
