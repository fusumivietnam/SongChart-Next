<?php

namespace Tests\Feature;

use App\Music\Providers\ProviderRequestGate;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

final class ProviderRequestGateTest extends TestCase
{
    use RefreshDatabase;

    public function test_independent_postgresql_workers_serialize_musicbrainz_acquisitions(): void
    {
        if (DB::getDriverName() !== 'pgsql') {
            $this->markTestSkipped('Cross-process gate verification requires PostgreSQL.');
        }

        // Each child bootstraps its own Laravel container and PDO connection.
        // An explicit READY/GO barrier keeps worker startup out of the timing proof.
        $workerCode = <<<'PHP'
require getcwd().'/vendor/autoload.php';
$app = require getcwd().'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
fwrite(STDOUT, "READY\n");
fflush(STDOUT);
if (fgets(STDIN) !== "GO\n") {
    exit(2);
}
app(App\Music\Providers\ProviderRequestGate::class)->acquire('musicbrainz');
fwrite(STDOUT, (string) round(microtime(true) * 1000)."\n");
fflush(STDOUT);
PHP;

        $workers = [];

        try {
            for ($index = 0; $index < 2; $index++) {
                $process = proc_open(
                    [PHP_BINARY, '-r', $workerCode],
                    [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
                    $pipes,
                    base_path(),
                );

                $this->assertIsResource($process, 'Unable to start independent PHP worker.');
                stream_set_timeout($pipes[1], 10);
                $workers[] = ['process' => $process, 'pipes' => $pipes];
            }

            foreach ($workers as $worker) {
                $ready = fgets($worker['pipes'][1]);
                $this->assertSame("READY\n", $ready, 'Provider gate worker failed to bootstrap.');
            }

            foreach ($workers as $worker) {
                fwrite($worker['pipes'][0], "GO\n");
                fflush($worker['pipes'][0]);
            }

            $acquisitions = [];
            foreach ($workers as $worker) {
                $timestamp = fgets($worker['pipes'][1]);
                $this->assertNotFalse($timestamp, 'Worker failed to acquire the provider gate.');
                $this->assertMatchesRegularExpression('/^\d+\n$/', $timestamp);
                $acquisitions[] = (int) trim($timestamp);
            }

            $this->assertGreaterThanOrEqual(
                850,
                abs($acquisitions[1] - $acquisitions[0]),
                'Independent PostgreSQL workers must not emit provider requests back-to-back.',
            );
        } finally {
            foreach ($workers as $worker) {
                foreach ($worker['pipes'] as $pipe) {
                    fclose($pipe);
                }

                if (proc_get_status($worker['process'])['running']) {
                    proc_terminate($worker['process']);
                }

                proc_close($worker['process']);
            }
        }
    }

    public function test_musicbrainz_gate_spaces_sequential_requests_by_at_least_one_second(): void
    {
        $gate = app(ProviderRequestGate::class);

        $gate->acquire('musicbrainz');
        $started = hrtime(true);
        $gate->acquire('musicbrainz');
        $elapsedMilliseconds = (hrtime(true) - $started) / 1_000_000;

        $this->assertGreaterThanOrEqual(
            850,
            $elapsedMilliseconds,
            'The deployment-wide gate must prevent requests from being emitted back-to-back.',
        );
    }
}
