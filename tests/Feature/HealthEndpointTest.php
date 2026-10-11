<?php

use Illuminate\Support\Facades\DB;
use RuntimeException;

test('health is healthy only when canonical database query succeeds', function (): void {
    $this->getJson('/health')
        ->assertOk()
        ->assertExactJson(['status' => 'ok']);
});

test('health fails closed without leaking database failure details', function (): void {
    DB::shouldReceive('selectOne')
        ->once()
        ->with('select 1 as healthy')
        ->andThrow(new RuntimeException('sensitive-db-host:5432 credential detail'));

    $response = $this->getJson('/health')
        ->assertStatus(503)
        ->assertExactJson(['status' => 'unavailable']);

    expect($response->getContent())
        ->not->toContain('sensitive-db-host')
        ->not->toContain('5432')
        ->not->toContain('credential')
        ->not->toContain('RuntimeException');
});
