from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_codespaces_workspace_bind_adr_is_present_and_accepted():
    text = (ROOT / "docs/adr/ADR-0010-codespaces-docker-outside-workspace-bind.md").read_text(encoding="utf-8")
    assert "Status: accepted" in text
    assert "${localWorkspaceFolder}" in text
    assert "${LOCAL_WORKSPACE_FOLDER:-.}" in text
    assert "Docker-outside" in text
