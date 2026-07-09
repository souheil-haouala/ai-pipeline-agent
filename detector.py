import os

def scan_workspace():
    """Scans the root project directory to dynamically identify the tech stack."""
    print("Initializing workspace ecosystem scan...")
    
    # Check for Python files and build dependencies
    if os.path.exists("requirements.txt") or os.path.exists("setup.py"):
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
        
    # Fallback default if nothing matches
    return {
        "stack": "Generic",
        "build_tool": "unknown"
    }

# This ensures the scan only runs locally if you execute this file directly
if __name__ == "__main__":
    result = scan_workspace()
    print(f"Scan complete! Found: {result['stack']} using {result['build_tool']}")
