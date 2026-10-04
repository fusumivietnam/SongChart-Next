<?php

namespace App\Music\Providers;

final class SystemProviderDelay implements ProviderDelay
{
    public function sleepMilliseconds(int $milliseconds): void
    {
        if ($milliseconds <= 0) {
            return;
        }

        usleep($milliseconds * 1000);
    }
}
