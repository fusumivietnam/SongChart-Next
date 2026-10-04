<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Models\ExternalIdentity;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ArtistFixtureCommandTest extends TestCase
{
    use RefreshDatabase;

    public function test_fixture_command_imports_the_same_artist_idempotently(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $firstId = Artist::query()->sole()->id;

        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();

        $this->assertSame($firstId, Artist::query()->sole()->id);
        $this->assertSame(1, Artist::query()->count());
        $this->assertSame(1, ExternalIdentity::query()->count());
    }
}
