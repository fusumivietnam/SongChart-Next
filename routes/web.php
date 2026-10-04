<?php

use App\Http\Controllers\ArtistController;
use Illuminate\Support\Facades\Route;

Route::inertia('/', 'welcome')->name('home');

Route::get('artists/{artist}/{slug?}', ArtistController::class)
    ->whereUlid('artist')
    ->name('artists.show');

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
