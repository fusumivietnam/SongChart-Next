<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('provider_request_gates', function (Blueprint $table): void {
            $table->string('provider')->primary();
            $table->timestampTz('next_allowed_at')->nullable();
            $table->timestampsTz();
        });

        DB::table('provider_request_gates')->insert([
            'provider' => 'musicbrainz',
            'next_allowed_at' => null,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        Schema::create('provider_evidence_blobs', function (Blueprint $table): void {
            $table->char('payload_hash', 64)->primary();
            $table->string('provider');
            $table->text('payload');
            $table->timestampTz('expires_at');
            $table->timestampsTz();

            $table->index(['provider', 'expires_at']);
        });

        Schema::create('provider_fetches', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('provider');
            $table->string('request_identity', 512);
            $table->timestampTz('fetched_at');
            $table->unsignedSmallInteger('http_status')->nullable();
            $table->string('schema_version');
            $table->char('payload_hash', 64)->nullable();
            $table->string('retention_class');
            $table->timestampTz('expires_at');
            $table->timestampsTz();

            $table->foreign('payload_hash')
                ->references('payload_hash')
                ->on('provider_evidence_blobs')
                ->nullOnDelete();
            $table->index(['provider', 'fetched_at']);
            $table->index('expires_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('provider_fetches');
        Schema::dropIfExists('provider_evidence_blobs');
        Schema::dropIfExists('provider_request_gates');
    }
};
