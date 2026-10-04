import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "design"


def test_design_authority_package_has_required_assets():
    required = [
        "DESIGN_AUTHORITY.md",
        "IDENTITY.md",
        "CONCEPT_CONTRACT.md",
        "PAGE_ARCHETYPES.md",
        "QUALITY_CONTRACT.md",
        "tokens/foundation.json",
        "components/COMPONENT_CONTRACTS.md",
        "patterns/SHELL.md",
        "patterns/ARTIST.md",
        "patterns/SEARCH.md",
        "patterns/RELEASE.md",
        "baselines/FOUNDATION.md",
        "decisions/FOUNDATION_BASELINE_APPROVAL.md",
    ]
    for relative in required:
        assert (DESIGN / relative).is_file(), relative


def test_foundation_lifecycle_labels_are_consistent():
    authority = (DESIGN / "DESIGN_AUTHORITY.md").read_text(encoding="utf-8")
    identity = (DESIGN / "IDENTITY.md").read_text(encoding="utf-8")
    tokens = json.loads((DESIGN / "tokens/foundation.json").read_text(encoding="utf-8"))

    assert "Foundation baseline approved on 2026-10-02" in authority
    assert "approved Foundation concept baseline since 2026-10-02" in identity
    assert tokens["status"] == "approved-foundation"
    assert tokens["approved_at"] == "2026-10-02"


def test_candidate_page_families_are_not_falsely_approved():
    archetypes = (DESIGN / "PAGE_ARCHETYPES.md").read_text(encoding="utf-8")
    for family in [
        "Release, Recording, Credits",
        "Home, category, tag, browse/discovery lists",
        "About, Terms, Privacy, Disclaimer",
        "404, 403, 500/service unavailable",
    ]:
        assert family in archetypes
    assert "candidate" in archetypes
    assert "generated mockup alone never advances lifecycle state" in archetypes


def test_ai_or_screenshot_reference_cannot_override_authority():
    authority = (DESIGN / "DESIGN_AUTHORITY.md").read_text(encoding="utf-8")
    concept = (DESIGN / "CONCEPT_CONTRACT.md").read_text(encoding="utf-8")
    assert "AI-generated image" in authority
    assert "cannot override" in concept


def test_quality_contract_keeps_narrow_and_wide_reference_sizes():
    quality = (DESIGN / "QUALITY_CONTRACT.md").read_text(encoding="utf-8")
    assert "390 × 844" in quality
    assert "1440 × 1024" in quality
    assert "visible focus" in quality
    assert "mixed-script" in quality
