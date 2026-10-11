from __future__ import annotations

import unittest
from pathlib import Path


class Vs04ReadinessContractTest(unittest.TestCase):
    def test_health_incident_runbook_has_required_boundaries(self) -> None:
        text = Path("docs/operations/VS04_HEALTH_INCIDENT.md").read_text()
        for phrase in (
            "GET /health",
            "HTTP 503",
            "no database hostname",
            "Stop and escalation conditions",
            "real G5 environment/deployment evidence recorded under #69",
        ):
            self.assertIn(phrase, text)

    def test_threat_model_covers_activated_and_deferred_risks(self) -> None:
        text = Path("docs/security/VS04_THREAT_MODEL.md").read_text()
        for phrase in (
            "External destination links",
            "no server-side fetch",
            "Corrections and support",
            "Provider data and canonical identity",
            "Secrets",
            "Health information disclosure",
            "Until #69 records real G5 environment/deployment evidence",
        ):
            self.assertIn(phrase, text)

    def test_release_record_fails_closed_before_real_g5(self) -> None:
        text = Path("docs/operations/VS04_RELEASE_READINESS.md").read_text()
        for phrase in (
            "launch is not declared",
            "G2 — public product/read journey",
            "G3 — security and release candidate",
            "G4 — operational and recovery readiness",
            "G5a — deployable single-VPS package",
            "STOP before production deployment",
            "Issue #69 remains open",
            "must not be described as `deployed`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
