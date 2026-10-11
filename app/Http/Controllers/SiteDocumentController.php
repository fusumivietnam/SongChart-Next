<?php

namespace App\Http\Controllers;

use Inertia\Inertia;
use Inertia\Response;

final class SiteDocumentController
{
    private const ISSUE_TRACKER_URL = 'https://github.com/fusumivietnam/SongChart-Next/issues/new';

    public function about(): Response
    {
        return $this->render('about', 'About SongChart Next', 'Music knowledge and discovery built around stable SongChart identity.', [
            ['heading' => 'What SongChart Next is', 'paragraphs' => [
                'SongChart Next is an internationally oriented music knowledge, metadata discovery and legal provider-navigation project.',
                'The public product focuses on canonical Artist, Release and Recording identities, structured credits, deterministic discovery and permitted external listening or viewing destinations.',
            ]],
            ['heading' => 'What it is not', 'paragraphs' => [
                'SongChart Next is not an audio or video hosting service, a social network, a recommendation engine or a general developer platform.',
                'Provider identifiers and URLs are evidence or navigation references. They do not replace stable SongChart canonical identity.',
            ]],
            ['heading' => 'Data quality', 'paragraphs' => [
                'Music metadata can be incomplete, disputed or change over time. SongChart keeps canonical decisions separate from provider claims and uses reviewable provenance where applicable.',
            ]],
        ]);
    }

    public function privacy(): Response
    {
        return $this->render('privacy', 'Privacy', 'The current public discovery experience does not require a public user account.', [
            ['heading' => 'Public browsing', 'paragraphs' => [
                'Public Artist, Release, Recording and discovery pages do not require registration, favorites, follows or a public profile.',
                'The application and its eventual hosting environment may technically process request metadata, security signals, cookies or logs needed to operate and protect the service. Production retention periods and infrastructure processors must be reviewed with the selected deployment environment before public launch.',
            ]],
            ['heading' => 'External destinations', 'paragraphs' => [
                'Following an external provider destination leaves SongChart. The destination provider operates under its own privacy and service terms.',
            ]],
            ['heading' => 'Support and corrections', 'paragraphs' => [
                'The initial public support and correction channel is the project issue tracker. Do not post passwords, access tokens, private account data or other sensitive personal information in a public issue.',
            ]],
        ]);
    }

    public function terms(): Response
    {
        return $this->render('terms', 'Terms of use', 'Use SongChart Next as an informational music-knowledge and discovery service.', [
            ['heading' => 'Informational metadata', 'paragraphs' => [
                'SongChart presents music metadata and canonical relationships for discovery and reference. Metadata may be incomplete, contested or corrected after review.',
            ]],
            ['heading' => 'External services', 'paragraphs' => [
                'External listening or viewing links are navigation references. SongChart does not redistribute provider audio or video by default and does not control an external provider after you leave SongChart.',
            ]],
            ['heading' => 'Acceptable use', 'paragraphs' => [
                'Do not use the service to interfere with availability, bypass access controls, submit secrets to public support channels or misrepresent provider data as a SongChart canonical decision.',
            ]],
            ['heading' => 'Launch status', 'paragraphs' => [
                'These terms describe the repository-owned launch-proof surface. A production deployment and its environment-specific operating terms remain separate release decisions until deployment evidence exists.',
            ]],
        ]);
    }

    public function disclaimer(): Response
    {
        return $this->render('disclaimer', 'Disclaimer', 'SongChart distinguishes canonical knowledge from provider evidence and external navigation.', [
            ['heading' => 'Metadata can change', 'paragraphs' => [
                'Music credits, dates, titles, relationships and other metadata can be incomplete or disputed. A displayed record is not a guarantee that every fact is final or uncontested.',
            ]],
            ['heading' => 'External links', 'paragraphs' => [
                'An external destination does not make that provider part of SongChart and does not imply endorsement, ownership or availability. External services can change independently.',
            ]],
            ['heading' => 'No media redistribution claim', 'paragraphs' => [
                'SongChart navigation to listening or viewing destinations does not grant SongChart ownership of provider media and does not imply permission to redistribute that media.',
            ]],
        ]);
    }

    public function support(): Response
    {
        return $this->render('support', 'Support', 'Report a reproducible SongChart problem through the public project issue tracker.', [
            ['heading' => 'What to include', 'paragraphs' => [
                'Include the SongChart URL, what you expected, what happened and enough non-sensitive detail to reproduce the problem.',
                'For metadata corrections, use the correction guidance so identity and evidence remain explicit.',
            ]],
            ['heading' => 'Keep secrets out of public issues', 'paragraphs' => [
                'Do not post passwords, tokens, private credentials or sensitive personal information. A public issue is not a confidential support channel.',
            ]],
        ], ['label' => 'Open the SongChart issue tracker', 'url' => self::ISSUE_TRACKER_URL]);
    }

    public function corrections(): Response
    {
        return $this->render('corrections', 'Corrections', 'Propose a metadata correction with canonical identity and supporting evidence.', [
            ['heading' => 'Identify the canonical record', 'paragraphs' => [
                'Include the SongChart Artist, Release or Recording URL and stable SongChart ID whenever possible. Do not rely on a display name alone to identify the record.',
            ]],
            ['heading' => 'Explain the proposed correction', 'paragraphs' => [
                'Describe the field or relationship that appears wrong, the proposed value and the evidence or provenance that supports the change.',
            ]],
            ['heading' => 'Review before canonical change', 'paragraphs' => [
                'A correction submission never writes canonical tables directly. Canonical changes require deterministic validation and the appropriate review decision.',
                'Do not include passwords, tokens or sensitive personal information in the public issue tracker.',
            ]],
        ], ['label' => 'Propose a correction', 'url' => self::ISSUE_TRACKER_URL]);
    }

    /**
     * @param list<array{heading:string,paragraphs:list<string>}> $sections
     * @param array{label:string,url:string}|null $action
     */
    private function render(string $slug, string $title, string $description, array $sections, ?array $action = null): Response
    {
        return Inertia::render('site/document', [
            'document' => [
                'slug' => $slug,
                'title' => $title,
                'description' => $description,
                'canonicalUrl' => url('/'.$slug),
                'sections' => $sections,
                'action' => $action,
            ],
        ]);
    }
}
