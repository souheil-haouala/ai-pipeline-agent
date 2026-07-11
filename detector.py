import os

def scan_workspace():
    """Scans the root project directory to dynamically identify the tech stack."""
    print("Initializing workspace ecosystem scan...")
    
    # Check for Docker environments first (infrastructure-as-code)
    if os.path.exists("Dockerfile") or os.path.exists("docker-compose.yml"):
        return {
            "stack": "Docker Containerization",
            "build_tool": "docker"
        }

    # Check for Python files and build dependencies
    if os.path.exists("requirements.txt") or os.path.exists("setup.py") or os.path.exists("pyproject.toml"):
        return {
            "stack": "Python",
            "build_tool": "pip"
        }
        
    # Check for Node.js files
    elif os.path.exists("package.json"):
        return {
            "stack": "Node.js",
            "build_tool": "npm"
        }

    # Check for Go environments
    elif os.path.exists("go.mod"):
        return {
            "stack": "Go",
            "build_tool": "go build"
        }

    # Check for Java build ecosystems
    elif os.path.exists("pom.xml"):
        return {
            "stack": "Java",
            "build_tool": "maven"
        }
    elif os.path.exists("build.gradle"):
        return {
            "stack": "Java/Kotlin",
            "build_tool": "gradle"
        }
        
    # Fallback default if nothing matches
    return {
        "stack": "Generic",
        "build_tool": "unknown"
    }

# This ensures the scan only runs locally if you execute this file directly
if __name__ == "__main__":
    result = scan_workspace()
    print(f"Scan complete! Found: {result['stack']} using {result['build_tool']}")
