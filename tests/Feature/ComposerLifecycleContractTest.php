<?php

namespace Tests\Feature;

use Tests\TestCase;

final class ComposerLifecycleContractTest extends TestCase
{
    public function test_composer_updates_do_not_reinstall_starter_features(): void
    {
        $composer = json_decode(file_get_contents(base_path('composer.json')), true, 512, JSON_THROW_ON_ERROR);

        $this->assertNotContains(
            '@php artisan install:features --ansi',
            $composer['scripts']['post-update-cmd'] ?? [],
        );
        $this->assertContains(
            '@php artisan vendor:publish --tag=laravel-assets --ansi --force',
            $composer['scripts']['post-update-cmd'] ?? [],
        );
        $this->assertContains(
            '@php artisan install:features --ansi',
            $composer['extra']['laravel']['installer']['post-create-project'] ?? [],
        );
    }
}
