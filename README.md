# AI Agent for Automated Application Pipeline Initialization

An autonomous, stack-agnostic DevOps orchestrator engine built for Software Engineering (Génie Logiciel) milestones. The framework dynamically evaluates workspace files to identify the underlying technology stack and instantly generates optimized, production-ready GitHub Actions CI/CD workflows utilizing generative AI model arrays.

## Core Features
- **Dynamic Workspace Scanning:** Programmatically parses environment states to distinguish between Python (pip) and Node.js (npm) ecosystems.
- **Context-Aware AI Generation:** Feeds discovered project parameters into Google Gemini models to construct precise testing matrices and artifact workflows.
- **Safe File Assembly:** Automatically provisions underlying system directories (`.github/workflows/`) and builds operational YAML assets cleanly on disk.
- **Robust System Error Isolation:** Gracefully catches network time-outs, parsing deadlocks, or credit limits.

## Project Architecture
- `main.py`: Central controller managing scanning, error interception, and network workflows.
- `detector.py`: Structural rule parser looking for ecosystem manifests (`package.json`, `requirements.txt`).
- `.env`: Protected storage isolating target application security credentials.

## Installation & Execution

1. Clone the project environment structure and access the root directory.
2. Configure your secret access credentials within a local `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_studio_api_key_here
   ```
3. Install required software dependencies via your local terminal interface:
   ```bash
   py -m pip install google-genai python-dotenv
   ```
4. Run the centralized engine orchestrator:
   ```bash
   py main.py
   ```
