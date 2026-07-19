# 🤖 Autonomous DevOps AI Pipeline Agent

An enterprise-grade AI DevOps engine designed for advanced software engineering automation. It audits local workspaces, ensures security, and generates validated GitHub Actions workflows using Google GenAI.

## ⚡ Core Features
*   **Intelligent Scanner (`detector.py`)**: Detects Python, Docker, Go, Java, and modern JS frameworks (React, Vue, Next) while avoiding nested test file corruption.
*   **Security Guardrail**: Implements a strict `SUPPORTED_STACKS` allowlist to prevent prompt injection.
*   **Schema Validation (`jsonschema`)**: Forces JSON output, validating against an immutable schema before generating YAML.
*   **Resiliency**: Features automatic 429 rate-limit handling with exponential backoff.
*   **Testing**: Includes a `pytest` suite for 100% test coverage without using live API tokens.

## 🏗 Project Architecture
```text
[Local Project] -> [detector.py] -> [main.py] -> [Allowlist/Schema] -> [GenAI] -> [ci.yml]
```

## 💻 Installation & Execution
**Docker (Recommended):**
1. Set `GEMINI_API_KEY` in `.env`.
2. `docker build -t ai-pipeline-agent:latest .`
3. `docker run --rm --env-file .env -v "$(pwd):/app/workspace" ai-pipeline-agent:latest`

**Local:**
1. `pip install -r requirements.txt`
2. `python main.py`

## 🌐 CI/CD
Fully integrated with GitHub Actions to ensure a green build history on every push.
