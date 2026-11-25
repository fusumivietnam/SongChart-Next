import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_devcontainer_exports_local_workspace_folder():
    config = json.loads((ROOT / ".devcontainer/devcontainer.json").read_text(encoding="utf-8"))
    assert config["remoteEnv"]["LOCAL_WORKSPACE_FOLDER"] == "${localWorkspaceFolder}"


def test_compose_uses_host_workspace_variable_for_app_source():
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert "${LOCAL_WORKSPACE_FOLDER:-.}:/var/www/html" in compose
    assert "- ./:/var/www/html" not in compose


def test_default_compose_only_publishes_required_app_port():
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert '127.0.0.1:8000:8000' in compose
    assert '127.0.0.1:5173:5173' not in compose
