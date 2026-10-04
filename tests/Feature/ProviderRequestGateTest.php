<?php

namespace Tests\Feature;

use App\Music\Providers\ProviderRequestGate;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ProviderRequestGateTest extends TestCase
{
    use RefreshDatabase;

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
