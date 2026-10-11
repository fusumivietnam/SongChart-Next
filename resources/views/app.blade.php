<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" @class(['dark' => ($appearance ?? 'system') == 'dark'])>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        {{-- Inline script to detect system dark mode preference and apply it immediately --}}
        <script>
            (function() {
                const appearance = '{{ $appearance ?? "system" }}';

                if (appearance === 'system') {
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

                    if (prefersDark) {
                        document.documentElement.classList.add('dark');
                    }
                }
            })();
        </script>

        {{-- Inline style to set the HTML background color based on our theme in app.css --}}
        <style>
            html {
                background-color: oklch(1 0 0);
            }

            html.dark {
                background-color: oklch(0.145 0 0);
            }
        </style>

        <link rel="icon" href="/favicon.ico" sizes="any">
        <link rel="icon" href="/favicon.svg" type="image/svg+xml">
        <link rel="apple-touch-icon" href="/apple-touch-icon.png">

        @fonts

        @viteReactRefresh
        @vite(['resources/css/app.css', 'resources/js/app.tsx', "resources/js/pages/{$page['component']}.tsx"])
        <x-inertia::head>
            <title>{{ config('app.name', 'Laravel') }}</title>
        </x-inertia::head>
    </head>
    <body class="font-sans antialiased">
        <x-inertia::app />

        @unless(request()->routeIs('dashboard') || request()->is('settings/*'))
            <footer class="border-t border-slate-300 bg-white text-slate-700" aria-label="Site information">
                <div class="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-7 text-sm sm:px-6 md:flex-row md:items-center md:justify-between">
                    <p class="font-medium text-slate-900">SongChart Next</p>
                    <nav aria-label="Supporting information">
                        <ul class="flex flex-wrap gap-x-4 gap-y-2">
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('about') }}">About</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('privacy') }}">Privacy</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('terms') }}">Terms</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('disclaimer') }}">Disclaimer</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('support') }}">Support</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('corrections') }}">Corrections</a></li>
                            <li><a class="rounded-sm hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" href="{{ route('sitemap') }}">Sitemap</a></li>
                        </ul>
                    </nav>
                </div>
            </footer>
        @endunless
    </body>
</html>
