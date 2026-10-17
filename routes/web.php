<?php

use App\Http\Controllers\ArtistController;
use App\Http\Controllers\CorrectionController;
use App\Http\Controllers\HealthController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\RecordingController;
use App\Http\Controllers\ReleaseController;
use App\Http\Controllers\SearchController;
use App\Http\Controllers\SeoController;
use App\Http\Controllers\SiteDocumentController;
use Illuminate\Support\Facades\Route;

Route::get('/', HomeController::class)->name('home');
Route::get('search', SearchController::class)->name('search');
Route::get('health', HealthController::class)->name('health');

Route::get('about', [SiteDocumentController::class, 'about'])->name('about');
Route::get('privacy', [SiteDocumentController::class, 'privacy'])->name('privacy');
Route::get('terms', [SiteDocumentController::class, 'terms'])->name('terms');
Route::get('disclaimer', [SiteDocumentController::class, 'disclaimer'])->name('disclaimer');
Route::get('support', [SiteDocumentController::class, 'support'])->name('support');
Route::get('corrections', [CorrectionController::class, 'show'])->name('corrections');
Route::post('corrections', [CorrectionController::class, 'store'])->name('corrections.store');
Route::get('robots.txt', [SeoController::class, 'robots'])->name('robots');
Route::get('sitemap.xml', [SeoController::class, 'sitemap'])->name('sitemap');

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
