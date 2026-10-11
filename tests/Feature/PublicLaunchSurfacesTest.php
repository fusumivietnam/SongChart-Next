<?php

namespace Tests\Feature;

use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class PublicLaunchSurfacesTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    public function test_supporting_documents_share_one_typed_public_anatomy(): void
    {
        $documents = [
            '/about' => 'About SongChart Next',
            '/privacy' => 'Privacy',
            '/terms' => 'Terms of use',
            '/disclaimer' => 'Disclaimer',
            '/support' => 'Support',
            '/corrections' => 'Corrections',
        ];

        foreach ($documents as $path => $title) {
            $this->get($path)
                ->assertOk()
                ->assertInertia(fn (Assert $page) => $page
                    ->component('site/document')
                    ->where('document.title', $title)
                    ->where('document.canonicalUrl', url($path))
                    ->has('document.sections'));
        }
    }

    public function test_correction_submission_is_review_only_and_uses_public_issue_tracker(): void
    {
        $this->get('/corrections')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('document.action.label', 'Propose a correction')
                ->where('document.action.url', 'https://github.com/fusumivietnam/SongChart-Next/issues/new')
                ->where('document.sections.2.heading', 'Review before canonical change')
                ->where('document.sections.2.paragraphs.0', 'A correction submission never writes canonical tables directly. Canonical changes require deterministic validation and the appropriate review decision.'));
    }

    public function test_support_warns_against_putting_secrets_in_public_issues(): void
    {
        $this->get('/support')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('document.action.label', 'Open the SongChart issue tracker')
                ->where('document.action.url', 'https://github.com/fusumivietnam/SongChart-Next/issues/new')
                ->where('document.sections.1.heading', 'Keep secrets out of public issues'));
    }

    public function test_public_shell_exposes_real_supporting_routes(): void
    {
        $response = $this->get('/about')->assertOk();

        foreach (['About', 'Privacy', 'Terms', 'Disclaimer', 'Support', 'Corrections', 'Sitemap'] as $label) {
            $response->assertSee($label);
        }
    }

    public function test_robots_points_to_the_repository_owned_sitemap(): void
    {
        $this->get('/robots.txt')
            ->assertOk()
            ->assertHeader('Content-Type', 'text/plain; charset=UTF-8')
            ->assertSeeText('User-agent: *')
            ->assertSeeText('Allow: /')
            ->assertSeeText('Sitemap: '.url('/sitemap.xml'));
    }

    public function test_sitemap_contains_only_activated_fixed_public_routes(): void
    {
        $response = $this->get('/sitemap.xml')
            ->assertOk()
            ->assertHeader('Content-Type', 'application/xml; charset=UTF-8');

        foreach (['/', '/search', '/about', '/privacy', '/terms', '/disclaimer', '/support', '/corrections'] as $path) {
            $response->assertSee(e(url($path)), false);
        }

        $response
            ->assertDontSee('/dashboard', false)
            ->assertDontSee('/settings/', false)
            ->assertDontSee('/artists/', false);
    }
}
