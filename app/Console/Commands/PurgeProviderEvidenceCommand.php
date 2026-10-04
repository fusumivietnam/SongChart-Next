<?php

namespace App\Console\Commands;

use App\Music\Providers\ProviderEvidenceStore;
use Illuminate\Console\Command;

final class PurgeProviderEvidenceCommand extends Command
{
    /** @var string */
    protected $signature = 'songchart:provider-evidence:purge';

    /** @var string */
    protected $description = 'Delete expired provider fetch evidence according to approved retention classes';

    public function handle(ProviderEvidenceStore $evidence): int
    {
        $deleted = $evidence->purgeExpired();
        $this->line("expired_fetches={$deleted['fetches']}");
        $this->line("expired_blobs={$deleted['blobs']}");

        return self::SUCCESS;
    }
}
