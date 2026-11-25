"""Regression contract for the local VS Code workspace-open startup."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_vscode_folder_open_uses_existing_safe_startup():
    task_file = ROOT / ".vscode" / "tasks.json"
    tasks = json.loads(task_file.read_text(encoding="utf-8"))["tasks"]
    assert len(tasks) == 2
    task = next(t for t in tasks if t["label"] == "SongChart: Auto Start")
    assert task["runOptions"]["runOn"] == "folderOpen"
    assert task["command"] == "bash"
    assert task["args"] == ["scripts/dev_up.sh"]
    assert task["options"]["cwd"] == "${workspaceFolder}"
    assert task["problemMatcher"] == []


def test_existing_healthy_app_checked_before_windows_listener_and_compose_up():
    script = (ROOT / "scripts" / "dev_up.sh").read_text(encoding="utf-8")
    detect = script.index('app_id="$(docker compose ps -q app')
    healthy = script.index('curl --fail --silent --show-error --max-time 5')
    windows = script.index('win_listener=')
    startup = script.index('docker compose up -d --wait db app')
    assert detect < healthy < windows < startup
    assert 'SongChart app already running; leaving containers untouched.' in script
    assert 'refusing to restart or switch ports automatically.' in script
    assert 'bash scripts/codespaces_public_read.sh' in script
    for forbidden in ('down -v', 'migrate:fresh', 'Stop-Process', 'kill -9', 'docker compose build'):
        assert forbidden not in script

def test_git_task_is_parallel_and_read_only():
    tasks = json.loads((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))["tasks"]
    task = next(t for t in tasks if t["label"] == "SongChart: Check Git Updates")
    assert task["runOptions"]["runOn"] == "folderOpen"
    assert task["args"] == ["scripts/git_workspace_status.sh"]
    assert task["command"] == "bash"
    assert task["options"]["cwd"] == "${workspaceFolder}"
    script = (ROOT / "scripts/git_workspace_status.sh").read_text(encoding="utf-8")
    assert "timeout 12s git" in script
    assert "git rev-list --left-right --count HEAD...refs/remotes/origin/main" in script
    assert "git status --porcelain" in script
    for forbidden in ("git pull ", "git merge ", "git reset ", "git stash ", "git checkout ", "git switch ", "git clean ", "git push "):
        assert not any(line.strip().startswith(forbidden) for line in script.splitlines())
