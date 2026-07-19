# 🤖 Autonomous DevOps AI Pipeline Agent

An enterprise-grade AI DevOps engine built in Python to dynamically generate and strictly validate type-safe GitHub Actions workflows. It safely audits local workspaces, protects configuration structures, and enforces robust system compliance gates.

## ⚡ Core Features

* **Intelligent Scanner (`detector.py`)**: Seamlessly scans multi-language project structures (Python, Go, Java, Docker, and modern JavaScript frameworks) while programmatically isolating vendor and dependency paths like `node_modules`.
* **Prompt Injection Defense**: Implements a strict `SUPPORTED_STACKS` validation allowlist to prevent untrusted inputs from manipulating pipeline instructions.
* **Deterministic Schema Verification**: Forces the underlying GenAI model to return structured telemetry, checking inputs against an immutable `jsonschema` layer before compiling final YAML files.
* **API Resiliency**: Incorporates custom exponential backoff logic to catch `429: RESOURCE_EXHAUSTED` rate limits smoothly without crashing execution tasks.
* **Robust Test Coverage**: Ships with an isolated, standalone `pytest` test harness simulating 10 distinct boundary constraints and adversarial conditions without exposing live API tokens.

## 🏗️ Project Architecture

```text
[Local Workspace Target] ──> [detector.py Scan] ──> [main.py Orchestration]
                                                             │
                                                     [JSONSchema Filter]
                                                             │
                                                     [Google GenAI Engine]
                                                             │
[Production Deployment] <── [Validated Verification] <── [Generated Output JSON]
```

## 💻 Boundary Stress Testing Matrix

The suite includes 10 automated unit test vectors tracking edge cases across execution zones:

1. **Schema Empty Checks**: Confirms structural schema keys reject empty object configurations.
2. **Adversarial Array Detection**: Rejects malicious data-type overrides targeting configuration headers.
3. **Self-Healing Mechanics**: Verifies regex parser strings cleanly isolate valid JSON hidden within messy raw markdown blocks.
4. **Empty Repositories**: Confirms the workspace scanner falls back cleanly to a Generic profile if zero files exist.
5. **Bloat Manifest Protection**: Prevents resource starvation loops by ignoring massive binary logs disguised as configuration files.
6. **Vendor Noise Insulation**: Disregards identical metadata patterns sitting deeply inside nested vendor trees (e.g., `node_modules`).
7. **Rate Limit Redundancy**: Simulates intense `429` server errors to confirm exponential sleep intervals work flawlessly.
8. **DevSecOps Credential Scans**: Programmatically blocks code compilation if exposed security strings or tokens are discovered in the file layout.
9. **Corrupted File Failbacks**: Reverts to an empty dictionary setup if local YAML files contain unclosed brackets or syntax flaws.
10. **Write-Locked System Resilience**: Prevents application crashes if the local target hard drive is out of space or read-only.

## ⚙️ Installation & Clean Run Commands

### Docker Sandbox Execution (Recommended)
1. Write your Google Studio token inside a local file: `echo "GEMINI_API_KEY=your_key" > .env`
2. Compile your application container: `docker build -t ai-pipeline-agent:latest .`
3. Execute localized generation routines safely: 
   ```bash
   docker run --rm --env-file .env -v "\$(pwd):/app/workspace" ai-pipeline-agent:latest
   ```

### Standard Local Execution
1. Install testing and pipeline framework requirements: `pip install -r requirements.txt`
2. Run your verification testing matrices completely green: `pytest`
3. Generate localized GitHub Actions workflow setups: `python main.py`
