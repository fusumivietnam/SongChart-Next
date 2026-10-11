import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class G5VpsBaselineTest(unittest.TestCase):
    def test_g5_vps_decision_is_explicit_and_bounded(self):
        text = (ROOT / "docs/adr/ADR-0015-single-vps-docker-production-baseline.md").read_text(encoding="utf-8")
        for phrase in (
            "Status: accepted for G5 preparation",
            "Ubuntu Server 24.04 LTS x86_64",
            "Docker Engine + Docker Compose",
            "PostgreSQL 18.6",
            "Coolify is not required",
            "must leave the VPS",
            "does not",
            "claim the application is deployed",
        ):
            self.assertIn(phrase, text)

    def test_production_compose_keeps_app_and_db_private(self):
        text = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
        self.assertIn("APP_IMAGE", text)
        self.assertIn("WEB_IMAGE", text)
        self.assertIn("postgres:18.6", text)
        self.assertIn("internal: true", text)
        self.assertIn("${HTTP_BIND_ADDRESS:-0.0.0.0}:${HTTP_PORT:-80}:8080", text)
        self.assertNotIn("5173", text)
        self.assertNotIn("artisan serve", text)
        self.assertNotIn("LOCAL_WORKSPACE_FOLDER", text)
        self.assertNotIn("/var/www/html:", text)

        db_block, rest = text.split("  app:\n", 1)
        app_block, web_block = rest.split("  web:\n", 1)
        self.assertNotIn("    ports:", db_block)
        self.assertNotIn("    ports:", app_block)
        self.assertIn("    ports:", web_block)

    def test_nginx_routes_php_only_to_private_app_service(self):
        text = (ROOT / "deploy/nginx/default.conf").read_text(encoding="utf-8")
        self.assertIn("listen 8080", text)
        self.assertIn("fastcgi_pass app:9000", text)
        self.assertIn("server_tokens off", text)
        self.assertIn("SCRIPT_FILENAME /var/www/html/public/index.php", text)

    def test_release_helpers_fail_closed_at_critical_boundaries(self):
        backup = (ROOT / "scripts/production/backup.sh").read_text(encoding="utf-8")
        rollback = (ROOT / "scripts/production/rollback.sh").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts/production/deploy.sh").read_text(encoding="utf-8")
        runbook = (ROOT / "docs/operations/VPS_PRODUCTION.md").read_text(encoding="utf-8")

        self.assertIn("OFF-HOST COPY REQUIRED", backup)
        self.assertIn("exit 3", backup)
        self.assertIn("@sha256:", rollback)
        self.assertIn("Database schema was NOT rolled back", rollback)
        self.assertIn("php artisan migrate --force", deploy)
        self.assertIn("a dump that remains on the same VPS is not a completed backup", runbook)
        self.assertIn("Never claim production recovery solely from CI evidence", runbook)

    def test_production_environment_example_contains_no_real_secret(self):
        text = (ROOT / "deploy/production.env.example").read_text(encoding="utf-8")
        self.assertIn("REPLACE_WITH_LARAVEL_APP_KEY", text)
        self.assertIn("REPLACE_WITH_UNIQUE_RANDOM_PASSWORD", text)
        self.assertIn("@sha256:REPLACE_ME", text)
        self.assertIn("HTTP_BIND_ADDRESS=127.0.0.1", text)


if __name__ == "__main__":
    unittest.main()
