<?php

namespace App\Http\Controllers;

use App\Music\Corrections\CorrectionEvidence;
use App\Music\Corrections\CorrectionSubjectType;
use App\Music\Corrections\SubmitCorrectionEvidence;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\RateLimiter;
use Inertia\Inertia;
use Inertia\Response;
use InvalidArgumentException;
use Symfony\Component\HttpFoundation\Response as HttpResponse;
use Throwable;

final class CorrectionController
{
    private const MAX_BODY_BYTES = 8192;

    private const SHORT_LIMIT = 5;

    private const SHORT_WINDOW_SECONDS = 600;

    private const DAILY_LIMIT = 20;

    private const DAILY_WINDOW_SECONDS = 86400;

    public function show(Request $request): Response
    {
        return $this->render($request->session()->pull('correctionStatus'));
    }

    public function store(Request $request, SubmitCorrectionEvidence $submitter): RedirectResponse|HttpResponse
    {
        $contentLength = (int) $request->server('CONTENT_LENGTH', 0);
        $bodyBytes = max($contentLength, strlen($request->getContent()));

        if ($bodyBytes > self::MAX_BODY_BYTES) {
            return $this->render('validation', null, 'The correction request is too large.')
                ->toResponse($request)
                ->setStatusCode(422);
        }

        $validated = $request->validate([
            'subject_type' => ['required', 'string', 'in:artist,release,recording'],
            'subject_id' => ['required', 'string', 'ulid'],
            'claim' => ['required', 'string', 'max:4000'],
            'evidence_url' => ['nullable', 'string', 'max:2048', 'url:http,https'],
        ]);

        $clientKey = hash_hmac(
            'sha256',
            ($request->ip() ?? 'unknown').'|'.($request->userAgent() ?? ''),
            (string) config('app.key'),
        );
        $shortKey = 'correction-intake:10m:'.$clientKey;
        $dailyKey = 'correction-intake:24h:'.$clientKey;

        if (RateLimiter::tooManyAttempts($shortKey, self::SHORT_LIMIT) || RateLimiter::tooManyAttempts($dailyKey, self::DAILY_LIMIT)) {
            $retryAfter = max(RateLimiter::availableIn($shortKey), RateLimiter::availableIn($dailyKey), 1);

            return $this->render('throttled', $retryAfter)
                ->toResponse($request)
                ->setStatusCode(429)
                ->header('Retry-After', (string) $retryAfter);
        }

        RateLimiter::hit($shortKey, self::SHORT_WINDOW_SECONDS);
        RateLimiter::hit($dailyKey, self::DAILY_WINDOW_SECONDS);

        try {
            $evidence = new CorrectionEvidence(
                CorrectionSubjectType::from($validated['subject_type']),
                $validated['subject_id'],
                $validated['claim'],
                $validated['evidence_url'] ?? null,
            );

            $submitter->submitDeduplicated($evidence);
        } catch (InvalidArgumentException) {
            return $this->render('validation', null, 'The canonical record could not be accepted for correction intake.')
                ->toResponse($request)
                ->setStatusCode(422);
        } catch (Throwable $exception) {
            Log::error('Public correction intake unavailable.', [
                'exception_class' => $exception::class,
            ]);

            return $this->render('unavailable')
                ->toResponse($request)
                ->setStatusCode(503);
        }

        return to_route('corrections')->with('correctionStatus', 'accepted');
    }

    private function render(?string $status = null, ?int $retryAfter = null, ?string $message = null): Response
    {
        return Inertia::render('site/document', [
            'document' => [
                'slug' => 'corrections',
                'title' => 'Corrections',
                'description' => 'Propose a metadata correction with canonical identity and supporting evidence.',
                'canonicalUrl' => url('/corrections'),
                'sections' => [
                    [
                        'heading' => 'Identify the canonical record',
                        'paragraphs' => [
                            'Choose Artist, Release or Recording and provide its stable SongChart ID. Do not rely on a display name alone to identify the record.',
                        ],
                    ],
                    [
                        'heading' => 'Explain the proposed correction',
                        'paragraphs' => [
                            'Describe what appears wrong and the proposed correction. You may add one public http/https evidence URL. SongChart stores that URL as submitted and does not fetch it during intake.',
                            'The initial intake does not ask for your name, email address, account or other contact identity. Do not submit passwords, tokens or sensitive personal information.',
                        ],
                    ],
                    [
                        'heading' => 'Review before canonical change',
                        'paragraphs' => [
                            'A correction submission never writes canonical tables directly. Submission only records pending evidence for later review and does not mean SongChart accepted the proposed canonical change.',
                            'Pending evidence is retained for at most 180 days. Resolved evidence and decision history are retained for at most 365 days after resolution under the approved intake policy.',
                        ],
                    ],
                ],
                'action' => null,
            ],
            'correctionIntake' => [
                'enabled' => true,
                'status' => $status,
                'retryAfter' => $retryAfter,
                'message' => $message,
                'limits' => [
                    'claimCharacters' => 4000,
                    'evidenceUrlCharacters' => 2048,
                    'requestBytes' => self::MAX_BODY_BYTES,
                ],
            ],
        ]);
    }
}
