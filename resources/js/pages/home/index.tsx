import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

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
                        <article key={`${item.type}-${item.id}`} className="grid gap-1 py-4 sm:grid-cols-[7rem_minmax(0,1fr)] sm:gap-4">
                            <div className="text-xs font-semibold tracking-[0.08em] text-blue-700 uppercase">{item.type}</div>
                            <div className="min-w-0">
                                <h3 className="text-base font-semibold break-words">
                                    <a
                                        href={item.path}
                                        className="rounded-sm text-blue-800 outline-none hover:underline focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                    >
                                        {item.name}
                                    </a>
                                </h3>
                                <p className="mt-1 break-words text-sm leading-6 text-slate-600">{item.detail}</p>
                            </div>
                        </article>
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
                    <div className="mx-auto flex max-w-[72rem] items-center px-4 py-4 sm:px-6">
                        <a
                            href="/"
                            className="rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>
                    </div>
                </header>

                <main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-10 sm:px-6">
                    <section className="max-w-4xl" aria-labelledby="home-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Canonical music discovery</p>
                        <h1 id="home-title" className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                            Music knowledge, from canonical data
                        </h1>
                        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
                            Search SongChart-owned Artist, Release and Recording identities, or explore a small deterministic sample of canonical records. Nothing here is personalized, ranked by popularity or inferred from provider links.
                        </p>

                        <form className="mt-7 flex max-w-2xl gap-2" action="/search" method="get" role="search">
                            <label htmlFor="home-search" className="sr-only">
                                Search music knowledge
                            </label>
                            <div className="relative min-w-0 flex-1">
                                <Search
                                    aria-hidden="true"
                                    className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-500"
                                />
                                <input
                                    id="home-search"
                                    name="q"
                                    maxLength={80}
                                    placeholder="Search artists, releases, recordings"
                                    className="h-11 w-full rounded-[0.625rem] border border-slate-300 bg-white pr-3 pl-9 text-sm outline-none placeholder:text-slate-500 focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"
                                />
                            </div>
                            <button
                                type="submit"
                                className="h-11 rounded-[0.625rem] bg-blue-700 px-4 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                            >
                                Search
                            </button>
                        </form>
                    </section>

                    <section className="mt-12 max-w-5xl" aria-labelledby="explore-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Deterministic discovery</p>
                        <h2 id="explore-title" className="mt-2 text-2xl font-semibold tracking-tight">
                            Explore canonical data
                        </h2>
                        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                            Each module is bounded and ordered alphabetically by canonical name or title with stable SongChart identity as the tie-breaker. These are not recommendations or popularity charts.
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
            </div>
        </>
    );
}
