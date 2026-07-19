# 🤖 Autonomous DevOps AI Pipeline Agent

# 🤖 Autonomous DevOps AI Pipeline Agent

![Node.js CI/CD Workflow](https://github.com)

An enterprise-grade, stack-agnostic AI DevOps orchestrator engine built for advanced Software Engineering automation.
An enterprise-grade, stack-agnostic AI DevOps orchestrator engine built for advanced Software Engineering automation. The framework dynamically audits local workspace structures using depth-intelligent pathing, passes evaluations through an anti-injection security firewall, and leverages the Google GenAI SDK to compile strictly validated, production-ready GitHub Actions workflows.

---

## ⚡ Core Features & Upgrades

- **Depth-Intelligent Multi-Language Scanner (`detector.py`):** Uses a shortest-path separator heuristic to accurately identify ecosystems (Python, Docker, Go, Java/Kotlin, Maven, Gradle) and modern Frontend/Node frameworks (React, Vue, Next.js, Angular, Nuxt) while preventing nested test files from corrupting root metrics.
- **Cyber-Security Allowlist Guardrail:** Implements a strict environment-to-build-tool matrix allowlist (`SUPPORTED_STACKS`) to completely eliminate prompt injection vulnerabilities.
- **Strict Schema Conformance Audit (`jsonschema`):** Forces Gemini into structured `application/json` response mode, validating the output against an immutable GitHub Actions JSON Schema before cleanly dumping standard YAML via `yaml.dump()` (100% immune to markdown formatting bugs).
- **Self-Healing Network Backoff:** Automatically intercepts `429 RESOURCE_EXHAUSTED` rate limits. Displays a live countdown timer in the console and uses exponential backoff to automatically heal socket connections.
- **Portable Standalone Binary Distribution:** Compiled via `PyInstaller` into a single, dependency-free executable (`pipeline-agent.exe`) that can be dragged, dropped, and executed instantly in any folder on any machine.
- **Zero-Token Offline Testing Suite (`pytest`):** Features a full unit testing layer with comprehensive directory and network client mocking, achieving 100% test passes in under 0.05 seconds without consuming live API tokens.

---

## 🏗️ Project Architecture

- `main.py`: Central orchestrator managing the visual CLI dashboard, network backoff loops, validation schemas, and IO disk streams.
- `detector.py`: Heuristic crawler parsing directory trees for framework manifests (`package.json`, `requirements.txt`, etc.).
- `tests/test_agent.py`: Isolated offline testing matrix mocking filesystem bounds and LLM handshakes.
- `requirements.txt`: Streamlined dependency index mapping required package versions.
- `.env`: Isolated storage panel mapping local security credentials.

---

## 💻 Installation & Execution

### Option 1: Running the Portable Binary (Recommended)
You can run the compiled agent instantly inside any code directory without needing Python or external dependencies:
1. Copy `pipeline-agent.exe` from the `dist/` directory.
2. Paste it into the root directory of your target software project.
3. Ensure a local `.env` file exists with your Google AI Studio credentials:
   ```env
   GEMINI_API_KEY=AIzaSyYourSecretKeyHere
   ```
4. Run the standalone tool in your terminal:
   ```powershell
   .\pipeline-agent.exe
   ```

### Option 2: Developer Environment Execution
To run the source code or continue expanding the framework:
1. Clone the repository and install the unified dependency manifest index:
   ```powershell
   pip install -r requirements.txt
   ```
2. Execute the local testing framework to ensure a stable baseline:
   ```powershell
   python -m pytest
   ```
3. Run the central automation orchestrator:
   ```powershell
   python main.py
   ```
4. Re-compile into a single executable binary using PyInstaller:
   ```powershell
   python -m PyInstaller --onefile --clean --collect-all google --name pipeline-agent main.py
   ```

---

## 🌐 Continuous Integration (CI/CD)

The project is fully integrated with a **GitHub Actions remote runner**. Every time code is pushed to this repository, the cloud container automatically boots up, installs the required workspace packages, safely injects your repository secrets, and triggers a full structural safety sweep to guarantee a completely green build history (`✓`).
