<?php

namespace App\Http\Controllers;

use App\Models\Recording;
use App\Music\Recordings\RecordingReadView;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

final class RecordingController
{
    public function __invoke(Recording $recording, RecordingReadView $view, ?string $slug = null): Response|RedirectResponse
    {
        if ($slug !== $recording->slug) {
            return redirect()->route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug], 301);
        }

        return Inertia::render('recordings/show', ['recording' => $view->get($recording)]);
    }
}
