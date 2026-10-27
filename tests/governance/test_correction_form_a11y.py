"""Guard the Corrections form's accessible validation-error associations."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[2] / "resources/js/pages/site/document.tsx").read_text(encoding="utf-8")


class CorrectionFormA11yTests(unittest.TestCase):
    def test_every_validation_error_has_field_association(self):
        for field, control in (
            ("subject_type", "subject-type"),
            ("subject_id", "subject-id"),
            ("claim", "claim"),
            ("evidence_url", "evidence-url"),
        ):
            with self.subTest(field=field):
                self.assertIn(f'aria-invalid={{Boolean(form.errors.{field})}}', SOURCE)
                self.assertIn(
                    f"aria-describedby={{form.errors.{field} ? '{control}-error' : undefined}}",
                    SOURCE,
                )
                self.assertIn(f'<p id="{control}-error"', SOURCE)


if __name__ == "__main__":
    unittest.main()
