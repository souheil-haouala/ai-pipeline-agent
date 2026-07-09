import os
from dotenv import load_dotenv
from google import genai
# Import your custom workspace scanner function from detector.py
from detector import scan_workspace

# Load credentials
load_dotenv()

# Initialize the Gemini Client
client = genai.Client()

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
            "You are an expert DevOps engineer. Provide ONLY the raw, valid YAML configuration content "
            f"for a GitHub Actions workflow (.github/workflows/main.yml) targeting a project built with {detected_stack} "
            f"using {build_tool}. Do not wrap your response in markdown code blocks like ```yaml or include any chat text."
        ),
    )

    yaml_content = response.text.strip()
    
    # Write the dynamic asset configuration directly to disk
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/main.yml", "w", encoding="utf-8") as f:
        f.write(yaml_content)
    
    print("\nSuccess! Infrastructure pipeline generated dynamically based on active code parameters.")

except Exception as e:
    print(f"\nAn error occurred during generation: {e}")
