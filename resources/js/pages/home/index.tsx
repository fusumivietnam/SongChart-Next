import { EntityResultRow } from '@/components/public-entity';
import { GlobalSearch, PublicShell } from '@/components/public-shell';
import { Head } from '@inertiajs/react';

type DiscoveryItem = {
    type: 'Artist' | 'Release' | 'Recording';
    id: string;
    name: string;
    detail: string;
    path: string;
};

type Props = {
    discovery: {
        artists: DiscoveryItem[];
        releases: DiscoveryItem[];
        recordings: DiscoveryItem[];
    };
};

type ModuleProps = {
    title: string;
    description: string;
    items: DiscoveryItem[];
};

function DiscoveryModule({ title, description, items }: ModuleProps) {
    return (
        <section aria-labelledby={`home-${title.toLowerCase()}`} className="border-t border-slate-300 pt-5">
            <div className="mb-4">
                <h2 id={`home-${title.toLowerCase()}`} className="text-lg font-semibold tracking-tight">
                    {title}
                </h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
            </div>
            {items.length > 0 ? (
                <div className="divide-y divide-slate-200 border-y border-slate-300">
                    {items.map((item) => (
                        <EntityResultRow key={`${item.type}-${item.id}`} item={item} discovery />
                    ))}
                </div>
            ) : (
                <p className="rounded-[0.875rem] border border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                    No canonical {title.toLowerCase()} are available yet.
                </p>
            )}
        </section>
    );
}

export default function HomeIndex({ discovery }: Props) {
    const hasDiscovery = discovery.artists.length + discovery.releases.length + discovery.recordings.length > 0;

    return (
        <>
            <Head title="SongChart Next — Music knowledge discovery" />
            <PublicShell home>

                <main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-10 sm:px-6">
                    <section className="rounded-[0.875rem] border border-slate-300 bg-slate-50 p-6 sm:p-8" aria-labelledby="home-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Canonical music discovery</p>
                        <h1 id="home-title" className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
                            Music knowledge, from canonical data
                        </h1>
                        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
                            Explore artists, releases and recordings through SongChart’s canonical music knowledge catalogue.
                        </p>

                        <GlobalSearch id="home-search" hero />
                    </section>

                    <section className="mt-12 max-w-5xl" aria-labelledby="explore-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Deterministic discovery</p>
                        <h2 id="explore-title" className="mt-2 text-2xl font-semibold tracking-tight">
                            Explore canonical data
                        </h2>
                        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                            Explore a bounded selection of canonical records, ordered alphabetically.
                        </p>

                        {!hasDiscovery && (
                            <div className="mt-6 rounded-[0.875rem] border border-slate-300 bg-slate-50 p-6">
                                <h3 className="font-semibold">No canonical discovery items yet</h3>
                                <p className="mt-2 text-sm leading-6 text-slate-600">
                                    SongChart does not invent discovery content when canonical records are unavailable. Search will become useful as canonical data is admitted.
                                </p>
                            </div>
                        )}

                        {hasDiscovery && (
                            <div className="mt-7 grid gap-8 lg:grid-cols-3">
                                <DiscoveryModule
                                    title="Artists"
                                    description="Canonical Artist identities, ordered by name."
                                    items={discovery.artists}
                                />
                                <DiscoveryModule
                                    title="Releases"
                                    description="Canonical Release identities, ordered by title."
                                    items={discovery.releases}
                                />
                                <DiscoveryModule
                                    title="Recordings"
                                    description="Canonical Recording identities, ordered by title."
                                    items={discovery.recordings}
                                />
                            </div>
                        )}
                    </section>
                </main>
            </PublicShell>
        </>
    );
}
