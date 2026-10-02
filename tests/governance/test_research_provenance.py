import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "governance" / "RESEARCH_REGISTRY.json"
NOTE = ROOT / "docs" / "research" / "RES-0001-musicbrainz-provider-constraints.md"


class ResearchProvenanceTests(unittest.TestCase):
    def test_res_0001_is_traceable_and_bounded(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        records = {item["id"]: item for item in data["research"]}
        record = records["RES-0001"]
        self.assertEqual(record["status"], "accepted")
        self.assertEqual(
            record["source"],
            "docs/research/RES-0001-musicbrainz-provider-constraints.md",
        )
        self.assertEqual(record["decision_ref"], "docs/providers/MUSICBRAINZ.md")
        self.assertEqual(
            record["capability_ids"],
            ["provider-policy", "provider-adapters"],
        )
        self.assertIsNone(record["superseded_by"])

    def test_research_note_has_minimum_provenance(self):
        text = NOTE.read_text(encoding="utf-8")
        required = [
            "Reviewed: 2026-10-02",
            "MusicBrainz / MetaBrainz Foundation",
            "https://musicbrainz.org/doc/MusicBrainz_API",
            "https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting",
            "https://musicbrainz.org/doc/About/Data_License",
            "Rights / security / privacy assessment",
            "Alternatives considered",
            "Limitations / unresolved decisions",
            "does **not** approve the provider adapter",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_registry_does_not_claim_chat_or_old_songchart_sources(self):
        data = REGISTRY.read_text(encoding="utf-8").lower()
        self.assertNotIn("chatgpt.com", data)
        self.assertNotIn("old songchart", data)
        self.assertNotIn(".zip", data)


if __name__ == "__main__":
    unittest.main()
