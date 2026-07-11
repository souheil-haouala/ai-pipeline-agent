import pytest
from detector import scan_workspace

def test_scan_workspace_detects_python(mocker):
    """Verifie que le scanner detecte Python lorsque requirements.txt existe."""
    # Mocking de os.path.exists pour intercepter l'appel systeme
    mock_exists = mocker.patch("os.path.exists")
    
    # Configuration du comportement simule : renvoie True uniquement pour requirements.txt
    mock_exists.side_effect = lambda path: path == "requirements.txt"
    
    result = scan_workspace()
    
    assert result["stack"] == "Python"
    assert result["build_tool"] == "pip"

def test_scan_workspace_detects_docker(mocker):
    """Verifie que le scanner detecte Docker en priorite absolue."""
    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = lambda path: path == "Dockerfile"
    
    result = scan_workspace()
    
    assert result["stack"] == "Docker Containerization"
    assert result["build_tool"] == "docker"

def test_scan_workspace_fallback_generic(mocker):
    """Verifie le comportement de repli si aucun fichier n'est trouve."""
    mock_exists = mocker.patch("os.path.exists")
    # Simule un dossier totalement vide (tous les fichiers renvoient False)
    mock_exists.return_value = False
    
    result = scan_workspace()
    
    assert result["stack"] == "Generic"
    assert result["build_tool"] == "unknown"
