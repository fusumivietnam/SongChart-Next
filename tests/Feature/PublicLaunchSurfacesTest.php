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

    public function test_correction_submission_is_internal_review_only_and_never_direct_canonical_write(): void
    {
        $this->get('/corrections')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('document.action', null)
                ->where('correctionIntake.enabled', true)
                ->where('document.sections.2.heading', 'Review before canonical change')
                ->where('document.sections.2.paragraphs.0', 'A correction submission never writes canonical tables directly. Submission only records pending evidence for later review and does not mean SongChart accepted the proposed canonical change.'));
    }

    public function test_correction_entry_prefills_only_valid_subject_pairs(): void
    {
        $id = '01ARZ3NDEKTSV4RRFFQ69G5FAV';

        foreach (['artist', 'release', 'recording'] as $type) {
            $this->get('/corrections?subject_type='.$type.'&subject_id='.$id)
                ->assertOk()
                ->assertInertia(fn (Assert $page) => $page
                    ->where('correctionIntake.subjectType', $type)
                    ->where('correctionIntake.subjectId', $id)
                    ->where('document.canonicalUrl', url('/corrections')));
        }

        foreach (['subject_type=work&subject_id='.$id, 'subject_type=release&subject_id=invalid', 'subject_type[]=artist&subject_id='.$id, 'subject_type=artist&subject_id[]=x', ''] as $query) {
            $this->get('/corrections?'.$query)
                ->assertOk()
                ->assertInertia(fn (Assert $page) => $page
                    ->where('correctionIntake.subjectType', 'artist')
                    ->where('correctionIntake.subjectId', ''));
        }
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
