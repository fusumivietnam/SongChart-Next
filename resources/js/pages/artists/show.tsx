import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

type Provenance = {
    provider: string;
    entity_type: string;
    external_id: string;
    source_name: string;
};

type RelatedRelease = {
    id: string;
    slug: string;
    title: string;
    status: string | null;
    countryCode: string | null;
    releaseYear: number | null;
    path: string;
};

type Artist = {
    id: string;
    slug: string;
    name: string;
    type: string | null;
    countryCode: string | null;
    disambiguation: string | null;
    provenance: Provenance[];
    releases: RelatedRelease[];
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

function releaseDetail(release: RelatedRelease): string {
    return [
        release.releaseYear?.toString(),
        release.status,
        release.countryCode,
    ]
        .filter((value): value is string => Boolean(value))
        .join(' · ');
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
                                    maxLength={80}
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

                            <section className="mt-6" aria-labelledby="artist-releases-heading">
                                <h2 id="artist-releases-heading" className="text-lg font-semibold">
                                    Releases and relationships
                                </h2>

                                {artist.releases.length === 0 ? (
                                    <div className="mt-3 rounded-[0.625rem] border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                                        No canonical release credits are recorded for this artist yet.
                                    </div>
                                ) : (
                                    <ul className="mt-3 divide-y divide-slate-200 border-y border-slate-300">
                                        {artist.releases.map((release) => {
                                            const detail = releaseDetail(release);

                                            return (
                                                <li key={release.id} className="py-4">
                                                    <a
                                                        href={release.path}
                                                        className="rounded-sm font-semibold text-blue-800 outline-none hover:underline focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                                    >
                                                        {release.title}
                                                    </a>
                                                    <p className="mt-1 text-sm leading-6 text-slate-600">
                                                        {detail || 'Canonical release credit'}
                                                    </p>
                                                </li>
                                            );
                                        })}
                                    </ul>
                                )}
                            </section>

                            <section className="mt-6 border-t border-slate-200 pt-5 text-sm text-slate-600">
                                <h2 className="font-semibold text-slate-900">
                                    Provenance and correction
                                </h2>
                                <p className="mt-2 leading-6">
                                    SongChart identity is independent from provider
                                    identity. Release relationships shown here come
                                    from canonical structured credits, never from a
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
