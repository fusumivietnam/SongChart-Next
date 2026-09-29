<?php

namespace Tests\Feature;

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
}
