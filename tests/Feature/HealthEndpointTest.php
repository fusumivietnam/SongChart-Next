<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\DB;
use RuntimeException;
use Tests\TestCase;

final class HealthEndpointTest extends TestCase
{
    public function test_health_is_healthy_only_when_canonical_database_query_succeeds(): void
    {
        $this->getJson('/health')
            ->assertOk()
            ->assertExactJson(['status' => 'ok']);
    }

    public function test_health_fails_closed_without_leaking_database_failure_details(): void
    {
        DB::shouldReceive('selectOne')
            ->once()
            ->with('select 1 as healthy')
            ->andThrow(new RuntimeException('sensitive-db-host:5432 credential detail'));

        $response = $this->getJson('/health')
            ->assertStatus(503)
            ->assertExactJson(['status' => 'unavailable']);

        $content = $response->getContent();

        self::assertStringNotContainsString('sensitive-db-host', $content);
        self::assertStringNotContainsString('5432', $content);
        self::assertStringNotContainsString('credential', $content);
        self::assertStringNotContainsString('RuntimeException', $content);
    }
}
