<?php

namespace App\Http\Controllers;

use App\Models\Artist;
use App\Music\Artists\ArtistReadView;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

final class ArtistController
{
    public function __invoke(Artist $artist, ?string $slug = null): Response|RedirectResponse
    {
        if ($slug !== $artist->slug) {
            return redirect()->route('artists.show', [
                'artist' => $artist->id,
                'slug' => $artist->slug,
            ], 301);
        }

        return Inertia::render('artists/show', [
            'artist' => ArtistReadView::fromArtist($artist)->toArray(),
        ]);
    }
}
