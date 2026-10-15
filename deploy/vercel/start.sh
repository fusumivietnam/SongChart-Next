#!/usr/bin/env sh
set -eu

if [ -n "${VERCEL_URL:-}" ]; then
  export APP_URL="https://${VERCEL_URL}"
fi

if [ -z "${APP_KEY:-}" ]; then
  echo "APP_KEY is required for preview runtime" >&2
  exit 1
fi

if [ -z "${DB_URL:-}" ]; then
  echo "DB_URL is required for preview runtime" >&2
  exit 1
fi

export PORT="${PORT:-3000}"
readiness_pid=""

cleanup_readiness() {
  if [ -n "${readiness_pid}" ]; then
    kill "${readiness_pid}" 2>/dev/null || true
    wait "${readiness_pid}" 2>/dev/null || true
    readiness_pid=""
  fi
}

trap cleanup_readiness EXIT INT TERM

php -S "0.0.0.0:${PORT}" /usr/local/bin/songchart-preview-readiness.php >/dev/null 2>&1 &
readiness_pid=$!

php -r '
$port = (int) getenv("PORT");
$deadline = microtime(true) + 5.0;
do {
    $socket = @fsockopen("127.0.0.1", $port, $errno, $errstr, 0.1);
    if ($socket !== false) {
        fclose($socket);
        exit(0);
    }
    usleep(50000);
} while (microtime(true) < $deadline);
fwrite(STDERR, "preview readiness gate failed to bind PORT\n");
exit(1);
'

/usr/local/bin/songchart-preview-bootstrap

cleanup_readiness
trap - EXIT INT TERM

exec php artisan serve --host=0.0.0.0 --port="${PORT}"
