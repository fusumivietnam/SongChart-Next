import { Head, useForm } from '@inertiajs/react';
import { ExternalLink, Search } from 'lucide-react';
import type { FormEvent } from 'react';

type Section = {
    heading: string;
    paragraphs: string[];
};

type DocumentAction = {
    label: string;
    url: string;
};

type CorrectionIntake = {
    enabled: boolean;
    status: 'accepted' | 'validation' | 'throttled' | 'unavailable' | null;
    retryAfter: number | null;
    message: string | null;
    limits: {
        claimCharacters: number;
        evidenceUrlCharacters: number;
        requestBytes: number;
    };
};

type Props = {
    document: {
        slug: string;
        title: string;
        description: string;
        canonicalUrl: string;
        sections: Section[];
        action: DocumentAction | null;
    };
    correctionIntake?: CorrectionIntake;
};

export default function SiteDocument({ document, correctionIntake }: Props) {
    const form = useForm({
        subject_type: 'artist',
        subject_id: '',
        claim: '',
        evidence_url: '',
    });

    function submitCorrection(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        form.post('/corrections', {
            preserveScroll: true,
            onSuccess: () => form.reset('claim', 'evidence_url'),
        });
    }

    const correctionStatus = correctionIntake?.status;

    return (
        <>
            <Head title={`${document.title} — SongChart Next`}>
                <meta name="description" content={document.description} />
                <link rel="canonical" href={document.canonicalUrl} />
            </Head>
            <div
                className="min-h-screen bg-white text-slate-900"
                style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}
            >
                <a
                    href="#main-content"
                    className="sr-only rounded-md bg-blue-700 px-3 py-2 text-white focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50"
                >
                    Skip to content
                </a>

                <header className="border-b border-slate-300 bg-white">
                    <div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-4 sm:px-6 md:flex-row md:items-center md:justify-between">
                        <a
                            href="/"
                            className="w-fit rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>
                        <form className="flex w-full max-w-md gap-2" action="/search" method="get" role="search">
                            <label htmlFor="site-search" className="sr-only">
                                Search music knowledge
                            </label>
                            <div className="relative min-w-0 flex-1">
                                <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-500" />
                                <input
                                    id="site-search"
                                    name="q"
                                    maxLength={80}
                                    placeholder="Search music knowledge"
                                    className="h-10 w-full rounded-[0.625rem] border border-slate-300 bg-white pr-3 pl-9 text-sm outline-none placeholder:text-slate-500 focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                />
                            </div>
                            <button
                                type="submit"
                                className="h-10 rounded-[0.625rem] bg-blue-700 px-4 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                            >
                                Search
                            </button>
                        </form>
                    </div>
                </header>

                <main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-10 sm:px-6">
                    <article className="max-w-3xl" aria-labelledby="document-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">SongChart Next</p>
                        <h1 id="document-title" className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                            {document.title}
                        </h1>
                        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">{document.description}</p>

                        <div className="mt-10 space-y-9">
                            {document.sections.map((section) => (
                                <section key={section.heading} className="border-t border-slate-300 pt-6">
                                    <h2 className="text-xl font-semibold tracking-tight">{section.heading}</h2>
                                    <div className="mt-3 space-y-3 text-[0.975rem] leading-7 text-slate-700">
                                        {section.paragraphs.map((paragraph) => (
                                            <p key={paragraph}>{paragraph}</p>
                                        ))}
                                    </div>
                                </section>
                            ))}
                        </div>

                        {correctionIntake?.enabled && (
                            <section className="mt-10 border-t border-slate-300 pt-6" aria-labelledby="correction-form-title">
                                <h2 id="correction-form-title" className="text-xl font-semibold tracking-tight">
                                    Submit correction evidence
                                </h2>
                                <p className="mt-2 text-sm leading-6 text-slate-600">
                                    No name, email address or public account is requested. Submitting evidence does not approve a canonical change.
                                </p>

                                {correctionStatus === 'accepted' && (
                                    <div role="status" className="mt-5 rounded-[0.625rem] border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-950">
                                        Correction evidence recorded for review. This does not mean the proposed canonical change was accepted.
                                    </div>
                                )}
                                {correctionStatus === 'validation' && (
                                    <div role="alert" className="mt-5 rounded-[0.625rem] border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                                        {correctionIntake.message ?? 'Check the correction fields and try again.'}
                                    </div>
                                )}
                                {correctionStatus === 'throttled' && (
                                    <div role="alert" className="mt-5 rounded-[0.625rem] border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                                        Too many correction attempts. Try again later{correctionIntake.retryAfter ? ` (about ${correctionIntake.retryAfter} seconds)` : ''}.
                                    </div>
                                )}
                                {correctionStatus === 'unavailable' && (
                                    <div role="alert" className="mt-5 rounded-[0.625rem] border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-950">
                                        Correction intake is temporarily unavailable. No canonical data was changed.
                                    </div>
                                )}

                                <form onSubmit={submitCorrection} className="mt-6 space-y-5" noValidate>
                                    <div>
                                        <label htmlFor="subject-type" className="block text-sm font-medium text-slate-900">
                                            Record type
                                        </label>
                                        <select
                                            id="subject-type"
                                            aria-invalid={Boolean(form.errors.subject_type)}
                                            aria-describedby={form.errors.subject_type ? 'subject-type-error' : undefined}
                                            value={form.data.subject_type}
                                            onChange={(event) => form.setData('subject_type', event.target.value)}
                                            className="mt-2 h-10 w-full rounded-[0.625rem] border border-slate-300 bg-white px-3 text-sm outline-none focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                        >
                                            <option value="artist">Artist</option>
                                            <option value="release">Release</option>
                                            <option value="recording">Recording</option>
                                        </select>
                                        {form.errors.subject_type && <p id="subject-type-error" className="mt-1 text-sm text-red-700">{form.errors.subject_type}</p>}
                                    </div>

                                    <div>
                                        <label htmlFor="subject-id" className="block text-sm font-medium text-slate-900">
                                            SongChart ID
                                        </label>
                                        <input
                                            id="subject-id"
                                            aria-invalid={Boolean(form.errors.subject_id)}
                                            aria-describedby={form.errors.subject_id ? 'subject-id-error' : undefined}
                                            value={form.data.subject_id}
                                            onChange={(event) => form.setData('subject_id', event.target.value)}
                                            autoComplete="off"
                                            required
                                            className="mt-2 h-10 w-full rounded-[0.625rem] border border-slate-300 bg-white px-3 font-mono text-sm outline-none focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                        />
                                        {form.errors.subject_id && <p id="subject-id-error" className="mt-1 text-sm text-red-700">{form.errors.subject_id}</p>}
                                    </div>

                                    <div>
                                        <label htmlFor="claim" className="block text-sm font-medium text-slate-900">
                                            Proposed correction
                                        </label>
                                        <textarea
                                            id="claim"
                                            aria-invalid={Boolean(form.errors.claim)}
                                            aria-describedby={form.errors.claim ? 'claim-error' : undefined}
                                            value={form.data.claim}
                                            onChange={(event) => form.setData('claim', event.target.value)}
                                            maxLength={correctionIntake.limits.claimCharacters}
                                            required
                                            rows={7}
                                            className="mt-2 w-full rounded-[0.625rem] border border-slate-300 bg-white px-3 py-2 text-sm leading-6 outline-none focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                        />
                                        <p className="mt-1 text-xs text-slate-500">Maximum {correctionIntake.limits.claimCharacters} characters.</p>
                                        {form.errors.claim && <p id="claim-error" className="mt-1 text-sm text-red-700">{form.errors.claim}</p>}
                                    </div>

                                    <div>
                                        <label htmlFor="evidence-url" className="block text-sm font-medium text-slate-900">
                                            Supporting public URL <span className="font-normal text-slate-500">(optional)</span>
                                        </label>
                                        <input
                                            id="evidence-url"
                                            aria-invalid={Boolean(form.errors.evidence_url)}
                                            aria-describedby={form.errors.evidence_url ? 'evidence-url-error' : undefined}
                                            type="url"
                                            value={form.data.evidence_url}
                                            onChange={(event) => form.setData('evidence_url', event.target.value)}
                                            maxLength={correctionIntake.limits.evidenceUrlCharacters}
                                            placeholder="https://example.org/source"
                                            className="mt-2 h-10 w-full rounded-[0.625rem] border border-slate-300 bg-white px-3 text-sm outline-none focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                        />
                                        <p className="mt-1 text-xs text-slate-500">Stored as submitted; SongChart does not fetch this URL during intake.</p>
                                        {form.errors.evidence_url && <p id="evidence-url-error" className="mt-1 text-sm text-red-700">{form.errors.evidence_url}</p>}
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={form.processing}
                                        className="inline-flex min-h-10 items-center rounded-[0.625rem] bg-blue-700 px-4 py-2.5 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                                    >
                                        {form.processing ? 'Submitting…' : 'Submit for review'}
                                    </button>
                                </form>
                            </section>
                        )}

                        {document.action && (
                            <div className="mt-10 border-t border-slate-300 pt-6">
                                <a
                                    href={document.action.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    referrerPolicy="no-referrer"
                                    className="inline-flex items-center gap-2 rounded-[0.625rem] bg-blue-700 px-4 py-2.5 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                >
                                    {document.action.label}
                                    <ExternalLink aria-hidden="true" className="h-4 w-4" />
                                </a>
                            </div>
                        )}
                    </article>
                </main>
            </div>
        </>
    );
}
