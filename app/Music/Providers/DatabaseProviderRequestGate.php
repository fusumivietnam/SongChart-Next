<?php

namespace App\Music\Providers;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Date;
use RuntimeException;

final readonly class DatabaseProviderRequestGate implements ProviderRequestGate
{
    public function __construct(private ProviderDelay $delay) {}

    public function acquire(string $provider): void
    {
        DB::transaction(function () use ($provider): void {
            $gate = DB::table('provider_request_gates')
                ->where('provider', $provider)
                ->lockForUpdate()
                ->first();

            if ($gate === null) {
                throw new RuntimeException("Provider request gate is not registered: {$provider}");
            }

            $nowMilliseconds = $this->nowMilliseconds();
            $nextAllowedAtMilliseconds = $gate->next_allowed_at_ms === null
                ? null
                : (int) $gate->next_allowed_at_ms;

            if ($nextAllowedAtMilliseconds !== null) {
                $this->delay->sleepMilliseconds(max(
                    0,
                    $nextAllowedAtMilliseconds - $nowMilliseconds,
                ));
            }

            DB::table('provider_request_gates')
                ->where('provider', $provider)
                ->update([
                    'next_allowed_at_ms' => $this->nowMilliseconds() + 1000,
                    'updated_at' => Date::now(),
                ]);
        }, 3);
    }

    private function nowMilliseconds(): int
    {
        return (int) floor(Date::now()->valueOf());
    }
}
