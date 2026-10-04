<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('artists', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('name');
            $table->string('slug');
            $table->string('type', 64)->nullable();
            $table->char('country_code', 2)->nullable();
            $table->text('disambiguation')->nullable();
            $table->timestamps();
        });

        Schema::create('external_identities', function (Blueprint $table): void {
            $table->id();
            $table->ulid('artist_id');
            $table->string('provider', 64);
            $table->string('entity_type', 64);
            $table->string('external_id', 191);
            $table->string('source_name');
            $table->json('provenance')->nullable();
            $table->timestamps();

            $table->foreign('artist_id')->references('id')->on('artists')->cascadeOnDelete();
            $table->unique(['provider', 'entity_type', 'external_id'], 'external_identity_unique');
            $table->index('artist_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('external_identities');
        Schema::dropIfExists('artists');
    }
};
