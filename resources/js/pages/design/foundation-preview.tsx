import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

type Surface =
    | 'artist'
    | 'artist-long'
    | 'search'
    | 'search-empty'
    | 'search-error';

type Props = {
    surface: Surface;
};

const normalArtist = {
    name: 'Aster Echo',
    type: 'Group',
    country: 'FI',
    disambiguation: 'Deterministic design fixture',
};

const longArtist = {
    name: '青い海 Orchestra — Ensemble for Transcontinental Night Sessions',
    type: 'Group',
    country: 'JP',
    disambiguation:
        'Long mixed-script deterministic fixture used to test wrapping and hierarchy',
};

const searchResults = [
    {
        type: 'Artist',
        name: 'Aster Echo',
        detail: 'Group · FI · deterministic fixture',
    },
    {
        type: 'Artist',
        name: 'Aster Echo',
        detail: 'Solo artist · CA · same-name disambiguation fixture',
    },
    {
        type: 'Release',
        name: 'Signals at Dawn',
        detail: 'Album · 2024 · Aster Echo',
    },
    {
        type: 'Recording',
        name: 'Signals at Dawn',
        detail: 'Recording · 4:12 · deterministic fixture',
    },
];

function FoundationShell({
    children,
    query = '',
}: {
    children: React.ReactNode;
    query?: string;
}) {
    return (
        <div
            className="min-h-screen bg-white text-slate-900"
            style={{
                fontFamily:
                    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            }}
        >
            <a
                href="#main-content"
                className="sr-only rounded-md bg-blue-700 px-3 py-2 text-white focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50"
            >
                Skip to content
            </a>

            <header className="border-b border-slate-300 bg-white">
                <div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-4 sm:px-6 md:flex-row md:items-center">
                    <div className="flex shrink-0 items-center justify-between">
                        <a
                            href="/_design/foundation/search"
                            className="rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>
                        <span className="text-xs text-slate-500 md:hidden">
                            Design candidate
                        </span>
                    </div>

                    <form
                        className="flex min-w-0 flex-1 gap-2"
                        action="/_design/foundation/search"
                        method="get"
                    >
                        <label htmlFor="site-search" className="sr-only">
                            Search music knowledge
                        </label>
                        <div className="relative min-w-0 flex-1">
                            <Search
                                aria-hidden="true"
                                className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-500"
                            />
                            <input
                                id="site-search"
                                name="q"
                                defaultValue={query}
                                placeholder="Search artists, releases, recordings"
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

                    <span className="hidden text-xs text-slate-500 md:inline">
                        Design candidate
                    </span>
                </div>
            </header>

            <main
                id="main-content"
                className="mx-auto w-full max-w-[72rem] px-4 py-8 sm:px-6"
            >
                {children}
            </main>
        </div>
    );
}

function ArtworkPlaceholder({ label }: { label: string }) {
    return (
        <div
            role="img"
            aria-label={label}
            className="flex aspect-square w-full items-center justify-center rounded-[0.875rem] border border-slate-300 bg-slate-100 text-center text-sm font-medium text-slate-500"
        >
            Artwork unavailable
        </div>
    );
}

function MetadataRow({
    label,
    value,
}: {
    label: string;
    value: string;
}) {
    return (
        <div className="grid grid-cols-[7rem_1fr] gap-3 border-t border-slate-200 py-3 text-sm first:border-t-0">
            <dt className="font-medium text-slate-600">{label}</dt>
            <dd className="min-w-0 text-slate-900">{value}</dd>
        </div>
    );
}

function ArtistSurface({ long = false }: { long?: boolean }) {
    const artist = long ? longArtist : normalArtist;

    return (
        <FoundationShell>
            <div className="mb-6">
                <p className="mb-2 text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">
                    Artist
                </p>
                <h1 className="max-w-4xl text-3xl leading-tight font-semibold tracking-tight break-words sm:text-4xl">
                    {artist.name}
                </h1>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                    {artist.disambiguation}
                </p>
            </div>

            <section
                aria-label="Artist identity"
                className="grid gap-6 md:grid-cols-[14rem_minmax(0,1fr)] md:items-start"
            >
                <ArtworkPlaceholder label="No artwork available for this design fixture" />

                <div className="min-w-0">
                    <dl className="rounded-[0.875rem] border border-slate-300 bg-white px-4">
                        <MetadataRow label="Type" value={artist.type} />
                        <MetadataRow label="Country" value={artist.country} />
                        <MetadataRow
                            label="SongChart ID"
                            value="art_fixture_01"
                        />
                        <MetadataRow
                            label="Provenance"
                            value="Deterministic design fixture — not canonical data"
                        />
                    </dl>

                    <section className="mt-6">
                        <h2 className="text-lg font-semibold">
                            Releases and relationships
                        </h2>
                        <div className="mt-3 rounded-[0.625rem] border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                            No release relationships are attached to this
                            design fixture.
                        </div>
                    </section>

                    <section className="mt-6 border-t border-slate-200 pt-5 text-sm text-slate-600">
                        <h2 className="font-semibold text-slate-900">
                            Provenance and correction
                        </h2>
                        <p className="mt-2 leading-6">
                            This screen uses controlled fixture data to review
                            hierarchy, missing-artwork behavior and responsive
                            layout. No provider destination is available.
                        </p>
                        <button
                            type="button"
                            className="mt-3 rounded-md text-sm font-medium text-blue-700 underline underline-offset-4 outline-none hover:text-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            Report a correction
                        </button>
                    </section>
                </div>
            </section>
        </FoundationShell>
    );
}

function SearchSurface({ state }: { state: 'results' | 'empty' | 'error' }) {
    return (
        <FoundationShell query={state === 'results' ? 'Aster Echo' : 'Unknown'}>
            <div className="max-w-4xl">
                <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">
                    Search
                </p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight">
                    Music knowledge results
                </h1>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                    Entity type and disambiguation stay visible so equal names
                    do not become name-only identity decisions.
                </p>

                {state === 'results' && (
                    <section aria-label="Search results" className="mt-7">
                        <div className="divide-y divide-slate-200 border-y border-slate-300">
                            {searchResults.map((result, index) => (
                                <article
                                    key={`${result.type}-${result.name}-${index}`}
                                    className="grid gap-1 py-4 sm:grid-cols-[7rem_minmax(0,1fr)] sm:gap-4"
                                >
                                    <div className="text-xs font-semibold tracking-[0.08em] text-blue-700 uppercase">
                                        {result.type}
                                    </div>
                                    <div className="min-w-0">
                                        <h2 className="text-base font-semibold break-words">
                                            {result.name}
                                        </h2>
                                        <p className="mt-1 text-sm leading-6 text-slate-600">
                                            {result.detail}
                                        </p>
                                    </div>
                                </article>
                            ))}
                        </div>
                    </section>
                )}

                {state === 'empty' && (
                    <section
                        aria-live="polite"
                        className="mt-7 rounded-[0.875rem] border border-slate-300 bg-slate-50 p-6"
                    >
                        <h2 className="font-semibold">No results</h2>
                        <p className="mt-2 text-sm leading-6 text-slate-600">
                            Try another artist, release or recording name.
                            Unknown data is not replaced with guessed matches.
                        </p>
                    </section>
                )}

                {state === 'error' && (
                    <section
                        role="alert"
                        className="mt-7 rounded-[0.875rem] border border-red-300 bg-red-50 p-6"
                    >
                        <h2 className="font-semibold text-red-900">
                            Search could not be completed
                        </h2>
                        <p className="mt-2 text-sm leading-6 text-red-800">
                            The failure is recoverable. No stale or fabricated
                            result is shown.
                        </p>
                        <button
                            type="button"
                            className="mt-4 rounded-[0.625rem] border border-red-300 bg-white px-3 py-2 text-sm font-medium text-red-900 outline-none hover:bg-red-100 focus-visible:ring-2 focus-visible:ring-red-700 focus-visible:ring-offset-2"
                        >
                            Retry search
                        </button>
                    </section>
                )}
            </div>
        </FoundationShell>
    );
}

export default function FoundationPreview({ surface }: Props) {
    const content = {
        artist: <ArtistSurface />,
        'artist-long': <ArtistSurface long />,
        search: <SearchSurface state="results" />,
        'search-empty': <SearchSurface state="empty" />,
        'search-error': <SearchSurface state="error" />,
    }[surface];

    return (
        <>
            <Head title="Foundation design preview" />
            {content}
        </>
    );
}
