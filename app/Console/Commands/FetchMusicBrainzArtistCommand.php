<?php

namespace App\Console\Commands;

use App\Music\Artists\ImportArtist;
use App\Music\Providers\MusicBrainz\MusicBrainzArtistClient;
use App\Music\Providers\ProviderFetchStatus;
use Illuminate\Console\Command;

final class FetchMusicBrainzArtistCommand extends Command
{
    /** @var string */
    protected $signature = 'songchart:musicbrainz:artist
        {mbid : MusicBrainz Artist UUID}
        {--admit : Explicitly pass a successful normalized claim to SongChart canonical admission}';

    /** @var string */
    protected $description = 'Fetch one MusicBrainz Artist through the approved VS-01b provider boundary';

    public function handle(MusicBrainzArtistClient $client, ImportArtist $importArtist): int
    {
        $mbid = (string) $this->argument('mbid');
        $result = $client->fetch($mbid);

        $this->line('status='.$result->status->value);
        if ($result->evidenceFetchId !== null) {
            $this->line('evidence_fetch_id='.$result->evidenceFetchId);
        }
        if ($result->errorCode !== null) {
            $this->line('error='.$result->errorCode);
        }

        if (! $result->succeeded() || $result->claim === null) {
            return $result->status === ProviderFetchStatus::NotFound
                ? self::SUCCESS
                : self::FAILURE;
        }

        $this->line('external_id='.$result->claim->externalId);
        $this->line('name='.$result->claim->name);

        if (! (bool) $this->option('admit')) {
            $this->comment('Canonical admission skipped; pass --admit explicitly to import this normalized claim.');

            return self::SUCCESS;
        }

        $artist = $importArtist->handle($result->claim);
        $this->info("admitted_artist_id={$artist->id}");

        return self::SUCCESS;
    }
}
