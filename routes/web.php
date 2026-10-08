<?php

use App\Http\Controllers\ArtistController;
use App\Http\Controllers\RecordingController;
use App\Http\Controllers\ReleaseController;
use App\Http\Controllers\SearchController;
use Illuminate\Support\Facades\Route;

Route::get('/', SearchController::class)->name('home');
Route::get('search', SearchController::class)->name('search');

Route::get('artists/{artist}/{slug?}', ArtistController::class)
    ->whereUlid('artist')
    ->name('artists.show');

Route::get('releases/{release}/{slug?}', ReleaseController::class)
    ->whereUlid('release')
    ->name('releases.show');

Route::get('recordings/{recording}/{slug?}', RecordingController::class)
    ->whereUlid('recording')
    ->name('recordings.show');

if (app()->environment(['local', 'testing'])) {
    Route::inertia('_design/foundation/artist', 'design/foundation-preview', [
        'surface' => 'artist',
    ])->name('design.foundation.artist');

    Route::inertia('_design/foundation/artist-long', 'design/foundation-preview', [
        'surface' => 'artist-long',
    ])->name('design.foundation.artist-long');

    Route::inertia('_design/foundation/search', 'design/foundation-preview', [
        'surface' => 'search',
    ])->name('design.foundation.search');

    Route::inertia('_design/foundation/search-empty', 'design/foundation-preview', [
        'surface' => 'search-empty',
    ])->name('design.foundation.search-empty');

    Route::inertia('_design/foundation/search-error', 'design/foundation-preview', [
        'surface' => 'search-error',
    ])->name('design.foundation.search-error');
}

Route::middleware(['auth', 'verified'])->group(function () {
    Route::inertia('dashboard', 'dashboard')->name('dashboard');
});

require __DIR__.'/settings.php';
