<?php

namespace App\Music\Providers;

use Carbon\CarbonImmutable;
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

            $now = Date::now();

            if ($gate->next_allowed_at !== null) {
                $nextAllowedAt = CarbonImmutable::parse((string) $gate->next_allowed_at);
                $waitMilliseconds = max(
                    0,
                    $nextAllowedAt->getTimestampMs() - $now->getTimestampMs(),
                );

                $this->delay->sleepMilliseconds($waitMilliseconds);
            }

            DB::table('provider_request_gates')
                ->where('provider', $provider)
                ->update([
                    'next_allowed_at' => Date::now()->addSecond(),
                    'updated_at' => Date::now(),
                ]);
        }, 3);
    }
}
