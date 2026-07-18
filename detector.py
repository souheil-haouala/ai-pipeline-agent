import os

def scan_workspace():
    """
    Scans the workspace recursively to dynamically identify the tech stack,
    handling sub-directories, case-sensitivity, and file extensions.
    """
    print("Initializing deep workspace ecosystem scan...")
    
    found_files = set()
    has_python_files = False

    # Walk recursively through directories, ignoring common heavy folders
    for root, dirs, files in os.walk("."):
        # Skip node_modules and virtual environments to save performance
        if any(ignored in root for ignored in ["node_modules", "venv", ".git", "__pycache__"]):
            continue
            
        for file in files:
            file_lower = file.lower()
            found_files.add(file_lower)
            
            if file_lower.endswith(".py"):
                has_python_files = True

    # 1. Check for Docker environments first
    if "dockerfile" in found_files or "docker-compose.yml" in found_files or "docker-compose.yaml" in found_files:
        return {"stack": "Docker Containerization", "build_tool": "docker"}

    # 2. Check for Python ecosystems
    if "requirements.txt" in found_files or "setup.py" in found_files or "pyproject.toml" in found_files:
        return {"stack": "Python", "build_tool": "pip"}

    # 3. Check for Node.js
    if "package.json" in found_files:
        return {"stack": "Node.js", "build_tool": "npm"}

    # 4. Check for Go
    if "go.mod" in found_files:
        return {"stack": "Go", "build_tool": "go build"}

    # 5. Check for Java/Kotlin
    if "pom.xml" in found_files:
        return {"stack": "Java", "build_tool": "maven"}
    if "build.gradle" in found_files or "build.gradle.kts" in found_files:
        return {"stack": "Java/Kotlin", "build_tool": "gradle"}
        
    # 6. Fallback to extension check if no manifest files exist
    if has_python_files:
        return {"stack": "Python (Scripting)", "build_tool": "python"}

    return {"stack": "Generic", "build_tool": "unknown"}

if __name__ == "__main__":
    result = scan_workspace()
    print(f"Scan complete! Found: {result['stack']} using {result['build_tool']}")
