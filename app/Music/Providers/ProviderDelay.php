<?php

namespace App\Music\Providers;

interface ProviderDelay
{
    public function sleepMilliseconds(int $milliseconds): void;
}
