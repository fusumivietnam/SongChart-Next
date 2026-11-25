<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class InternalOperatorAccessTest extends TestCase
{
    use RefreshDatabase;

    public function test_new_users_default_to_no_operator_access(): void
    {
        $user = User::factory()->create();

        $this->assertFalse($user->fresh()->is_super_admin);
        $this->assertFalse($user->hasOperatorAccess());
    }

    public function test_verified_and_confirmed_two_factor_identity_can_be_provisioned_and_revoked(): void
    {
        $user = User::factory()->create([
            'email_verified_at' => now(),
        ]);
        $user->forceFill(['two_factor_confirmed_at' => now()])->save();

        $this->artisan('songchart:operator:access', [
            'user' => (string) $user->id,
            '--force' => true,
        ])->assertExitCode(0);

        $this->assertTrue($user->fresh()->hasOperatorAccess());

        $this->artisan('songchart:operator:access', [
            'user' => (string) $user->id,
            '--revoke' => true,
            '--force' => true,
        ])->assertExitCode(0);

        $this->assertFalse($user->fresh()->hasOperatorAccess());
    }

    public function test_unverified_or_unconfirmed_identity_cannot_be_granted_access(): void
    {
        $unverified = User::factory()->unverified()->create();
        $unconfirmed = User::factory()->create();

        foreach ([$unverified, $unconfirmed] as $user) {
            $this->artisan('songchart:operator:access', [
                'user' => (string) $user->id,
                '--force' => true,
            ])->assertExitCode(1);

            $this->assertFalse($user->fresh()->is_super_admin);
        }
    }

    public function test_missing_user_is_rejected_without_creating_an_account(): void
    {
        $this->artisan('songchart:operator:access', [
            'user' => '99999999',
            '--force' => true,
        ])->assertExitCode(1);

        $this->assertSame(0, User::query()->count());
    }

    public function test_user_cannot_self_assign_operator_access_through_mass_assignment(): void
    {
        $user = User::factory()->create();
        $this->assertFalse($user->isFillable('is_super_admin'));
        $this->assertFalse($user->fresh()->is_super_admin);
    }

    public function test_operator_access_fails_closed_if_verification_or_two_factor_is_removed(): void
    {
        $user = User::factory()->create();
        $user->forceFill([
            'is_super_admin' => true,
            'two_factor_confirmed_at' => now(),
        ])->save();

        $this->assertTrue($user->hasOperatorAccess());

        $user->forceFill(['two_factor_confirmed_at' => null])->save();
        $this->assertFalse($user->hasOperatorAccess());

        $user->forceFill([
            'two_factor_confirmed_at' => now(),
            'email_verified_at' => null,
        ])->save();
        $this->assertFalse($user->hasOperatorAccess());
    }
}
