<?php

namespace App\Console\Commands;

use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use Illuminate\Console\Command;
use JsonException;
use RuntimeException;

final class ImportReleaseFixtureCommand extends Command
{
    /** @var string */
    protected $signature = 'songchart:fixture:import-release {path? : Path to deterministic MusicBrainz-shaped release bundle JSON}';

    /** @var string */
    protected $description = 'Import the deterministic VS-02 Release/Recording/Credits fixture';

    /** @throws JsonException */
    public function handle(MusicBrainzReleaseBundleNormalizer $normalizer, ImportReleaseBundle $importer): int
    {
        $pathArgument = $this->argument('path');
        $path = is_string($pathArgument) && $pathArgument !== ''
            ? $pathArgument
            : base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json');

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
            throw new RuntimeException('Release fixture must decode to a JSON object.');
        }

        /** @var array<string,mixed> $decoded */
        $release = $importer->handle($normalizer->normalize($decoded));
        $this->info("Imported Release {$release->id} ({$release->title})");
        $this->line(route('releases.show', ['release' => $release->id, 'slug' => $release->slug], false));
        return self::SUCCESS;
    }
}
