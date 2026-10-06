<?php

namespace App\Http\Controllers;

use App\Models\Release;
use App\Music\Releases\ReleaseReadView;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

final class ReleaseController
{
    public function __invoke(Release $release, ?string $slug, ReleaseReadView $view): Response|RedirectResponse
    {
        if ($slug !== $release->slug) {
            return redirect()->route('releases.show', ['release' => $release->id, 'slug' => $release->slug], 301);
        }

        return Inertia::render('releases/show', ['release' => $view->get($release)]);
    }
}
