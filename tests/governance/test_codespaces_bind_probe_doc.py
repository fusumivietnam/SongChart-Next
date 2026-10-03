from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_codespaces_bind_probe_does_not_recommend_destructive_volume_cleanup():
    text = (ROOT / "docs/operations/CODESPACES_BIND_PROBE.md").read_text(encoding="utf-8")
    assert "docker inspect" in text
    assert "Do not hard-code" in text
    assert "do not delete named volumes" in text
