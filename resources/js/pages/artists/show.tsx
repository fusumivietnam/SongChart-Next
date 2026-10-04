import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

type Provenance = {
    provider: string;
    entity_type: string;
    external_id: string;
    source_name: string;
};

type Artist = {
    id: string;
    slug: string;
    name: string;
    type: string | null;
    countryCode: string | null;
    disambiguation: string | null;
    provenance: Provenance[];
};

type Props = {
    artist: Artist;
};

function MetadataRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="grid grid-cols-[7rem_1fr] gap-3 border-t border-slate-200 py-3 text-sm first:border-t-0">
            <dt className="font-medium text-slate-600">{label}</dt>
            <dd className="min-w-0 break-words text-slate-900">{value}</dd>
        </div>
    );
}

export default function ArtistShow({ artist }: Props) {
    const primarySource = artist.provenance[0];

    return (
        <>
            <Head title={`${artist.name} — SongChart Next`} />

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
                        <a
                            href="/"
                            className="shrink-0 rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>

                        <form
                            className="flex min-w-0 flex-1 gap-2"
                            action="/"
                            method="get"
                            role="search"
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
                    </div>
                </header>

                <main
                    id="main-content"
                    className="mx-auto w-full max-w-[72rem] px-4 py-8 sm:px-6"
                >
                    <div className="mb-6">
                        <p className="mb-2 text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">
                            Artist
                        </p>
                        <h1 className="max-w-4xl text-3xl leading-tight font-semibold tracking-tight break-words sm:text-4xl">
                            {artist.name}
                        </h1>
                        {artist.disambiguation && (
                            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                                {artist.disambiguation}
                            </p>
                        )}
                    </div>

                    <section
                        aria-label="Artist identity"
                        className="grid gap-6 md:grid-cols-[14rem_minmax(0,1fr)] md:items-start"
                    >
                        <div
                            role="img"
                            aria-label={`Artwork unavailable for ${artist.name}`}
                            className="flex aspect-square w-full items-center justify-center rounded-[0.875rem] border border-slate-300 bg-slate-100 p-4 text-center text-sm font-medium text-slate-500"
                        >
                            Artwork unavailable
                        </div>

                        <div className="min-w-0">
                            <dl className="rounded-[0.875rem] border border-slate-300 bg-white px-4">
                                <MetadataRow
                                    label="Type"
                                    value={artist.type ?? 'Unknown'}
                                />
                                <MetadataRow
                                    label="Country"
                                    value={artist.countryCode ?? 'Unknown'}
                                />
                                <MetadataRow label="SongChart ID" value={artist.id} />
                                <MetadataRow
                                    label="Provenance"
                                    value={
                                        primarySource
                                            ? `${primarySource.provider} · ${primarySource.external_id}`
                                            : 'No external provenance recorded'
                                    }
                                />
                            </dl>

                            <section className="mt-6">
                                <h2 className="text-lg font-semibold">
                                    Releases and relationships
                                </h2>
                                <div className="mt-3 rounded-[0.625rem] border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                                    No release relationships are available in the
                                    fixture-first Artist slice.
                                </div>
                            </section>

                            <section className="mt-6 border-t border-slate-200 pt-5 text-sm text-slate-600">
                                <h2 className="font-semibold text-slate-900">
                                    Provenance and correction
                                </h2>
                                <p className="mt-2 leading-6">
                                    SongChart identity is independent from provider
                                    identity. The source identifier is retained as
                                    provenance evidence and is never replaced by a
                                    name-only match.
                                </p>
                                <button
                                    type="button"
                                    disabled
                                    className="mt-3 rounded-md text-sm font-medium text-slate-500 underline underline-offset-4 disabled:cursor-not-allowed"
                                >
                                    Report a correction — workflow not active yet
                                </button>
                            </section>
                        </div>
                    </section>
                </main>
            </div>
        </>
    );
}
