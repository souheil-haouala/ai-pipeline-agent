import os
import json

def scan_workspace():
    """
    Scans the workspace recursively to dynamically identify the tech stack,
    handling sub-directories, case-sensitivity, file extensions, and frontend frameworks.
    """
    print("Initializing deep workspace ecosystem scan...")
    
    found_files = {}
    has_python_files = False

    # Walk recursively through directories, ignoring common heavy folders
    for root, dirs, files in os.walk("."):
        # Skip node_modules and virtual environments to save performance
        if any(ignored in root for ignored in ["node_modules", "venv", ".git", "__pycache__", "dist", ".next"]):
            continue
            
        for file in files:
            file_lower = file.lower()
            # Store the full relative file path mapped to its lower name for target reading
            found_files[file_lower] = os.path.join(root, file)
            
            if file_lower.endswith(".py"):
                has_python_files = True

    # 1. Advanced Node.js / Frontend Framework Detection
    if "package.json" in found_files:
        build_tool = "npm"
        if "lock.yaml" in found_files or "pnpm-lock.yaml" in found_files:
            build_tool = "pnpm"
        elif "yarn.lock" in found_files:
            build_tool = "yarn"

        # Safely open package.json ONLY if the file actually exists on the disk
        package_json_path = found_files["package.json"]
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    if "next" in dependencies:
                        return {"stack": "Next.js Framework", "build_tool": f"{build_tool} run build"}
                    if "react" in dependencies:
                        return {"stack": "React Frontend", "build_tool": f"{build_tool} run build"}
                    if "vue" in dependencies:
                        return {"stack": "Vue Frontend", "build_tool": f"{build_tool} run build"}
                    if "@angular/core" in dependencies:
                        return {"stack": "Angular Frontend", "build_tool": f"{build_tool} run build"}
                    if "nuxt" in dependencies:
                        return {"stack": "Nuxt Framework", "build_tool": f"{build_tool} run build"}
            except Exception:
                pass # Fallback to standard Node if JSON parsing crashes

        return {"stack": "Node.js Application", "build_tool": build_tool}

    # 2. Check for Docker environments
    if "dockerfile" in found_files or "docker-compose.yml" in found_files or "docker-compose.yaml" in found_files:
        return {"stack": "Docker Containerization", "build_tool": "docker"}

    # 3. Check for Python ecosystems
    if "requirements.txt" in found_files or "setup.py" in found_files or "pyproject.toml" in found_files:
        return {"stack": "Python", "build_tool": "pip"}

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
