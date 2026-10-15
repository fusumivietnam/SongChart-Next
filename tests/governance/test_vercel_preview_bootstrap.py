from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class VercelPreviewBootstrapContractTest(unittest.TestCase):
    def test_startup_binds_readiness_before_bootstrap_and_hands_off_to_laravel(self) -> None:
        start = (ROOT / "deploy/vercel/start.sh").read_text()

        gate = 'php -S "0.0.0.0:${PORT}" /usr/local/bin/songchart-preview-readiness.php'
        bootstrap = "/usr/local/bin/songchart-preview-bootstrap"
        laravel = 'exec php artisan serve --host=0.0.0.0 --port="${PORT}"'

        self.assertIn(gate, start)
        self.assertIn(bootstrap, start)
        self.assertIn(laravel, start)
        self.assertLess(start.index(gate), start.index(bootstrap))
        self.assertLess(start.index(bootstrap), start.index(laravel))
        self.assertNotIn("php artisan migrate --force", start)
        self.assertNotIn("songchart:fixture:import-artist", start)
        self.assertNotIn("songchart:fixture:import-release", start)

    def test_bootstrap_owns_migrations_and_deterministic_fixtures(self) -> None:
        bootstrap = (ROOT / "deploy/vercel/bootstrap.sh").read_text()

        self.assertIn("php artisan migrate --force --no-interaction", bootstrap)
        self.assertIn("php artisan config:clear", bootstrap)
        self.assertIn("songchart:fixture:import-artist --no-interaction", bootstrap)
        self.assertIn("songchart:fixture:import-release --no-interaction", bootstrap)
        self.assertIn('PREVIEW_SEED_FIXTURES:-true', bootstrap)

    def test_readiness_gate_is_fail_closed_and_non_cacheable(self) -> None:
        readiness = (ROOT / "deploy/vercel/readiness.php").read_text()

        self.assertIn("http_response_code(503)", readiness)
        self.assertIn("Retry-After: 2", readiness)
        self.assertIn("Cache-Control: no-store", readiness)
        self.assertIn("bootstrapping", readiness)

    def test_preview_image_packages_supervised_startup_contract(self) -> None:
        dockerfile = (ROOT / "Dockerfile.vercel").read_text()

        self.assertIn("COPY deploy/vercel/start.sh /usr/local/bin/songchart-preview-start", dockerfile)
        self.assertIn("COPY deploy/vercel/bootstrap.sh /usr/local/bin/songchart-preview-bootstrap", dockerfile)
        self.assertIn("COPY deploy/vercel/readiness.php /usr/local/bin/songchart-preview-readiness.php", dockerfile)
        self.assertIn('CMD ["songchart-preview-start"]', dockerfile)


if __name__ == "__main__":
    unittest.main()
