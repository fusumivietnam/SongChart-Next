from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_g5_vps_decision_is_explicit_and_bounded():
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
        assert phrase in text


def test_production_compose_keeps_app_and_db_private():
    text = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
    assert "APP_IMAGE" in text
    assert "WEB_IMAGE" in text
    assert "postgres:18.6" in text
    assert "internal: true" in text
    assert "${HTTP_BIND_ADDRESS:-0.0.0.0}:${HTTP_PORT:-80}:8080" in text
    assert "5173" not in text
    assert "artisan serve" not in text
    assert "LOCAL_WORKSPACE_FOLDER" not in text
    assert "/var/www/html:" not in text

    db_block, rest = text.split("  app:\n", 1)
    app_block, web_block = rest.split("  web:\n", 1)
    assert "    ports:" not in db_block
    assert "    ports:" not in app_block
    assert "    ports:" in web_block


def test_nginx_routes_php_only_to_private_app_service():
    text = (ROOT / "deploy/nginx/default.conf").read_text(encoding="utf-8")
    assert "listen 8080" in text
    assert "fastcgi_pass app:9000" in text
    assert "server_tokens off" in text
    assert "SCRIPT_FILENAME /var/www/html/public/index.php" in text


def test_release_helpers_fail_closed_at_critical_boundaries():
    backup = (ROOT / "scripts/production/backup.sh").read_text(encoding="utf-8")
    rollback = (ROOT / "scripts/production/rollback.sh").read_text(encoding="utf-8")
    deploy = (ROOT / "scripts/production/deploy.sh").read_text(encoding="utf-8")
    runbook = (ROOT / "docs/operations/VPS_PRODUCTION.md").read_text(encoding="utf-8")

    assert "OFF-HOST COPY REQUIRED" in backup
    assert "exit 3" in backup
    assert "@sha256:" in rollback
    assert "Database schema was NOT rolled back" in rollback
    assert "php artisan migrate --force" in deploy
    assert "a dump that remains on the same VPS is not a completed backup" in runbook
    assert "Never claim production recovery solely from CI evidence" in runbook


def test_production_environment_example_contains_no_real_secret():
    text = (ROOT / "deploy/production.env.example").read_text(encoding="utf-8")
    assert "REPLACE_WITH_LARAVEL_APP_KEY" in text
    assert "REPLACE_WITH_UNIQUE_RANDOM_PASSWORD" in text
    assert "@sha256:REPLACE_ME" in text
    assert "HTTP_BIND_ADDRESS=127.0.0.1" in text
