<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('correction_submissions', function (Blueprint $table): void {
            $table->ulid('id')->primary();
            $table->string('subject_type', 32);
            $table->ulid('subject_id');
            $table->text('claim');
            $table->text('evidence_url')->nullable();
            $table->string('status', 32)->default('pending');
            $table->timestamps();

            $table->index(['subject_type', 'subject_id']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('correction_submissions');
    }
};
