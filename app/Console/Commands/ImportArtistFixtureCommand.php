<?php

namespace App\Console\Commands;

use App\Music\Artists\ImportArtist;
use App\Music\Artists\MusicBrainzArtistNormalizer;
use Illuminate\Console\Command;
use JsonException;
use RuntimeException;

final class ImportArtistFixtureCommand extends Command
{
    /** @var string */
    protected $signature = 'songchart:fixture:import-artist {path? : Path to a MusicBrainz-shaped Artist JSON fixture}';

    /** @var string */
    protected $description = 'Import a deterministic MusicBrainz-shaped Artist fixture into canonical SongChart storage';

    /** @throws JsonException */
    public function handle(MusicBrainzArtistNormalizer $normalizer, ImportArtist $importArtist): int
    {
        $pathArgument = $this->argument('path');
        $path = is_string($pathArgument) && $pathArgument !== ''
            ? $pathArgument
            : base_path('database/fixtures/musicbrainz/artist-aster-echo.json');

        if (! is_file($path)) {
            $this->error("Fixture not found: {$path}");

            return self::FAILURE;
        }

        $json = file_get_contents($path);
        if ($json === false) {
            throw new RuntimeException("Unable to read fixture: {$path}");
        }

        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        if (! is_array($decoded)) {
            throw new RuntimeException('Artist fixture must decode to a JSON object.');
        }

        /** @var array<string, mixed> $decoded */
        $artist = $importArtist->handle($normalizer->normalize($decoded));

        $this->info("Imported Artist {$artist->id} ({$artist->name})");
        $this->line(route('artists.show', ['artist' => $artist->id, 'slug' => $artist->slug], false));

        return self::SUCCESS;
    }
}
