<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('release_groups', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('title');
            $table->string('slug');
            $table->string('primary_type', 64)->nullable();
            $table->text('disambiguation')->nullable();
            $table->timestamps();
        });

        Schema::create('releases', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->ulid('release_group_id')->nullable();
            $table->string('title');
            $table->string('slug');
            $table->string('status', 64)->nullable();
            $table->char('country_code', 2)->nullable();
            $table->unsignedSmallInteger('release_year')->nullable();
            $table->unsignedTinyInteger('release_month')->nullable();
            $table->unsignedTinyInteger('release_day')->nullable();
            $table->string('date_precision', 16)->nullable();
            $table->string('barcode', 64)->nullable();
            $table->timestamps();

            $table->foreign('release_group_id')->references('id')->on('release_groups')->nullOnDelete();
            $table->index(['release_group_id', 'release_year']);
        });

        Schema::create('recordings', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('title');
            $table->string('slug');
            $table->unsignedInteger('length_ms')->nullable();
            $table->text('disambiguation')->nullable();
            $table->timestamps();
        });

        Schema::create('works', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('title');
            $table->string('slug');
            $table->string('type', 64)->nullable();
            $table->text('disambiguation')->nullable();
            $table->timestamps();
        });

        Schema::create('music_external_identities', function (Blueprint $table): void {
            $table->id();
            $table->string('canonical_type', 64);
            $table->ulid('canonical_id');
            $table->string('provider', 64);
            $table->string('entity_type', 64);
            $table->string('external_id', 191);
            $table->string('source_name');
            $table->json('provenance')->nullable();
            $table->timestamps();

            $table->unique(['provider', 'entity_type', 'external_id'], 'music_external_identity_unique');
            $table->index(['canonical_type', 'canonical_id']);
        });

        Schema::create('recording_isrcs', function (Blueprint $table): void {
            $table->id();
            $table->ulid('recording_id');
            $table->string('isrc', 16)->unique();
            $table->timestamps();

            $table->foreign('recording_id')->references('id')->on('recordings')->cascadeOnDelete();
        });

        Schema::create('release_media', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->ulid('release_id');
            $table->unsignedSmallInteger('position');
            $table->string('format', 64)->nullable();
            $table->string('title')->nullable();
            $table->timestamps();

            $table->foreign('release_id')->references('id')->on('releases')->cascadeOnDelete();
            $table->unique(['release_id', 'position']);
        });

        Schema::create('release_tracks', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->ulid('medium_id');
            $table->ulid('recording_id');
            $table->unsignedSmallInteger('position');
            $table->string('number', 32);
            $table->string('title');
            $table->unsignedInteger('length_ms')->nullable();
            $table->timestamps();

            $table->foreign('medium_id')->references('id')->on('release_media')->cascadeOnDelete();
            $table->foreign('recording_id')->references('id')->on('recordings')->restrictOnDelete();
            $table->unique(['medium_id', 'position']);
        });

        Schema::create('entity_credits', function (Blueprint $table): void {
            $table->id();
            $table->string('subject_type', 64);
            $table->ulid('subject_id');
            $table->ulid('artist_id');
            $table->string('role', 64);
            $table->string('credited_as');
            $table->string('join_phrase', 32)->default('');
            $table->unsignedSmallInteger('position');
            $table->timestamps();

            $table->foreign('artist_id')->references('id')->on('artists')->restrictOnDelete();
            $table->unique(['subject_type', 'subject_id', 'position'], 'entity_credit_subject_position_unique');
            $table->index(['artist_id', 'role']);
        });

        Schema::create('recording_work', function (Blueprint $table): void {
            $table->ulid('recording_id');
            $table->ulid('work_id');
            $table->string('relationship_type', 64)->default('performance');
            $table->timestamps();

            $table->foreign('recording_id')->references('id')->on('recordings')->cascadeOnDelete();
            $table->foreign('work_id')->references('id')->on('works')->cascadeOnDelete();
            $table->primary(['recording_id', 'work_id', 'relationship_type']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('recording_work');
        Schema::dropIfExists('entity_credits');
        Schema::dropIfExists('release_tracks');
        Schema::dropIfExists('release_media');
        Schema::dropIfExists('recording_isrcs');
        Schema::dropIfExists('music_external_identities');
        Schema::dropIfExists('works');
        Schema::dropIfExists('recordings');
        Schema::dropIfExists('releases');
        Schema::dropIfExists('release_groups');
    }
};
