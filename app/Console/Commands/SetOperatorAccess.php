<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;

class SetOperatorAccess extends Command
{
    protected $signature = 'songchart:operator:access
        {user : Existing internal user ID}
        {--revoke : Revoke operator access}
        {--force : Skip interactive confirmation}';

    protected $description = 'Provision or revoke internal operator identity (not correction review authorization)';

    public function handle(): int
    {
        $id = (string) $this->argument('user');

        if (! ctype_digit($id) || (int) $id < 1) {
            $this->error('Provide an existing numeric user ID.');

            return self::FAILURE;
        }

        $user = User::query()->find((int) $id);

        if (! $user) {
            $this->error('User not found; no account was created.');

            return self::FAILURE;
        }

        $revoke = (bool) $this->option('revoke');

        if (! $revoke && (! $user->hasVerifiedEmail() || $user->two_factor_confirmed_at === null)) {
            $this->error('Grant denied: the internal identity must have verified email and confirmed 2FA.');

            return self::FAILURE;
        }

        if (! $this->option('force') && ! $this->confirm(
            ($revoke ? 'Revoke' : 'Grant').' operator access for user ID '.$user->getKey().'?',
            false,
        )) {
            $this->warn('No change made.');

            return self::FAILURE;
        }

        $user->forceFill(['is_super_admin' => ! $revoke])->save();

        $this->info('Operator access '.($revoke ? 'revoked' : 'granted').' for user ID '.$user->getKey().'.');
        $this->warn('This does not enable correction review, canonical writes, or any unapproved admin routes.');

        return self::SUCCESS;
    }
}
