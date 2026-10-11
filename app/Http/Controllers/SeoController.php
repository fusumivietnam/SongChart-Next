<?php

namespace App\Http\Controllers;

use Illuminate\Http\Response;

final class SeoController
{
    /** @var list<string> */
    private const FIXED_PUBLIC_PATHS = [
        '/',
        '/search',
        '/about',
        '/privacy',
        '/terms',
        '/disclaimer',
        '/support',
        '/corrections',
    ];

    public function robots(): Response
    {
        return response(
            "User-agent: *\nAllow: /\nSitemap: ".url('/sitemap.xml')."\n",
            200,
            ['Content-Type' => 'text/plain; charset=UTF-8']
        );
    }

    public function sitemap(): Response
    {
        $urls = array_map(
            static fn (string $path): string => '  <url><loc>'.e(url($path)).'</loc></url>',
            self::FIXED_PUBLIC_PATHS
        );

        $xml = implode("\n", [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ...$urls,
            '</urlset>',
            '',
        ]);

        return response($xml, 200, ['Content-Type' => 'application/xml; charset=UTF-8']);
    }
}
