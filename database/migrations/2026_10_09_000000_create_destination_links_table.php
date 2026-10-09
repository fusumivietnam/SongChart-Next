<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('destination_links', function (Blueprint $table): void {
            $table->id();
            $table->string('subject_type', 32);
            $table->ulid('subject_id');
            $table->string('provider', 64);
            $table->string('destination_type', 16);
            $table->text('external_url');
            $table->char('external_url_hash', 64);
            $table->string('source_name', 128);
            $table->string('source_reference', 191)->nullable();
            $table->json('provenance')->nullable();
            $table->string('verification_state', 16);
            $table->timestampTz('verified_at')->nullable();
            $table->timestamps();

            $table->unique(
                ['subject_type', 'subject_id', 'provider', 'destination_type', 'external_url_hash'],
                'destination_links_subject_provider_url_unique'
            );
            $table->index(
                ['subject_type', 'subject_id', 'verification_state'],
                'destination_links_subject_state_index'
            );
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('destination_links');
    }
};
