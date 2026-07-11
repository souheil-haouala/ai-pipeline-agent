import pytest
from detector import scan_workspace

def test_scan_workspace_detects_python(mocker):
    """Vérifie que le scanner détecte Python lorsque requirements.txt existe."""
    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = lambda path: path == "requirements.txt"
    
    result = scan_workspace()
    
    assert result["stack"] == "Python"
    assert result["build_tool"] == "pip"

def test_scan_workspace_detects_docker(mocker):
    """Vérifie que le scanner détecte Docker en priorité absolue."""
    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = lambda path: path == "Dockerfile"
    
    result = scan_workspace()
    
    assert result["stack"] == "Docker Containerization"
    assert result["build_tool"] == "docker"

def test_scan_workspace_detects_nodejs(mocker):
    """Vérifie que le scanner détecte Node.js lorsque package.json existe."""
    mock_exists = mocker.patch("os.path.exists")
    # Simule que package.json est présent, mais pas les fichiers Python ou Docker
    mock_exists.side_effect = lambda path: path == "package.json"
    
    result = scan_workspace()
    
    assert result["stack"] == "Node.js"
    assert result["build_tool"] == "npm"

def test_scan_workspace_detects_java_maven(mocker):
    """Vérifie que le scanner détecte Java via l'outil de build Maven."""
    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = lambda path: path == "pom.xml"
    
    result = scan_workspace()
    
    assert result["stack"] == "Java"
    assert result["build_tool"] == "maven"

def test_scan_workspace_fallback_generic(mocker):
    """Vérifie le comportement de repli si aucun fichier n'est trouvé."""
    mock_exists = mocker.patch("os.path.exists")
    mock_exists.return_value = False
    
    result = scan_workspace()
    
    assert result["stack"] == "Generic"
    assert result["build_tool"] == "unknown"
