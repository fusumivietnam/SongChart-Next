<?php

namespace App\Music\Providers;

interface ProviderRequestGate
{
    public function acquire(string $provider): void;
}
