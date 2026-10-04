import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TECH = ROOT / "governance" / "TECHNOLOGY_REGISTRY.json"
POLICY = ROOT / "docs" / "providers" / "MUSICBRAINZ.md"


class MusicBrainzPolicyTests(unittest.TestCase):
    def test_provider_policy_contract_exists(self):
        text = POLICY.read_text(encoding="utf-8")
        required = [
            "one MusicBrainz request per second",
            "meaningful User-Agent",
            "core/CC0",
            "supplementary",
            "commercial/public production remains blocked",
            "Owner decision B1",
            "30 days",
            "7 days",
            "503 responses are retryable only with bounded exponential backoff and jitter",
            "bounded live probe",
            "must not",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_musicbrainz_is_registered_for_bounded_noncommercial_evaluation(self):
        data = json.loads(TECH.read_text(encoding="utf-8"))
        entries = {item["id"]: item for item in data["technologies"]}
        entry = entries["musicbrainz-web-service"]
        self.assertEqual(entry["capability"], "provider-adapters")
        self.assertEqual(entry["status"], "implemented")
        self.assertEqual(
            entry["implementation"],
            "app/Music/Providers/MusicBrainz/MusicBrainzArtistClient.php",
        )
        scope = entry["scope"].lower()
        self.assertIn(">=1 second", scope)
        self.assertIn("live access disabled by default", scope)
        self.assertIn("no commercial production approval", scope)

    def test_no_cover_art_or_supplementary_activation(self):
        text = POLICY.read_text(encoding="utf-8").lower()
        self.assertIn("cover art archive assets under this review", text)
        self.assertIn("supplementary musicbrainz data", text)


if __name__ == "__main__":
    unittest.main()
