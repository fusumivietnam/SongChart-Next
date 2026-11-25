import { ArtworkPlaceholder, MetadataRow } from '@/components/public-entity';
import { PublicShell } from '@/components/public-shell';
import { Head } from '@inertiajs/react';

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

            <PublicShell>

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
                        <ArtworkPlaceholder name={artist.name} />

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
                                <a
                                    href={`/corrections?subject_type=artist&subject_id=${artist.id}`}
                                    className="mt-3 inline-block rounded-sm text-sm font-medium text-blue-700 underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                >
                                    Report a correction
                                </a>
                            </section>
                        </div>
                    </section>
                </main>
            </PublicShell>
        </>
    );
}
