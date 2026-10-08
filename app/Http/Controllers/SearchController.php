<?php

namespace App\Http\Controllers;

use App\Music\Discovery\DiscoverySearch;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

final class SearchController
{
    public function __invoke(Request $request, DiscoverySearch $search): Response
    {
        return Inertia::render('search/index', [
            'search' => $search->search($request->query('q'))->toArray(),
        ]);
    }
}
