<?php

namespace Tests\Feature;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

class FoundationDesignPreviewTest extends TestCase
{
    public function test_foundation_design_preview_routes_render_deterministic_surfaces(): void
    {
        $surfaces = [
            'design.foundation.artist' => 'artist',
            'design.foundation.artist-long' => 'artist-long',
            'design.foundation.search' => 'search',
            'design.foundation.search-empty' => 'search-empty',
            'design.foundation.search-error' => 'search-error',
        ];

        foreach ($surfaces as $route => $surface) {
            $this->get(route($route))
                ->assertOk()
                ->assertInertia(fn (Assert $page) => $page
                    ->component('design/foundation-preview')
                    ->where('surface', $surface));
        }
    }

    public function test_local_preview_trusts_standard_reverse_proxy_headers(): void
    {
        Route::get('/_test/foundation-proxy', function (Request $request) {
            return response()->json([
                'scheme' => $request->getScheme(),
                'host' => $request->getHost(),
                'url' => url('/_design/foundation/artist'),
            ]);
        });

        $this
            ->withServerVariables(['REMOTE_ADDR' => '127.0.0.1'])
            ->withHeaders([
                'X-Forwarded-Host' => 'songchart-preview.example.test',
                'X-Forwarded-Proto' => 'https',
                'X-Forwarded-Port' => '443',
            ])
            ->get('/_test/foundation-proxy')
            ->assertOk()
            ->assertJson([
                'scheme' => 'https',
                'host' => 'songchart-preview.example.test',
                'url' => 'https://songchart-preview.example.test/_design/foundation/artist',
            ]);
    }
}
