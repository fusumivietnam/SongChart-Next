<?php

namespace App\Http\Controllers;

use App\Music\Discovery\HomeDiscovery;
use Inertia\Inertia;
use Inertia\Response;

final class HomeController
{
    public function __invoke(HomeDiscovery $discovery): Response
    {
        return Inertia::render('home/index', [
            'discovery' => $discovery->toArray(),
        ]);
    }
}
