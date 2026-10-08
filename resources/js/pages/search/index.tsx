import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

type SearchItem = {
    type: 'Artist' | 'Release' | 'Recording';
    id: string;
    slug: string;
    name: string;
    detail: string;
    path: string;
};

type Props = {
    search: {
        query: string;
        items: SearchItem[];
    };
};

export default function SearchIndex({ search }: Props) {
    const hasQuery = search.query.length > 0;

    return (
        <>
            <Head title={hasQuery ? `${search.query} — Search — SongChart Next` : 'Search — SongChart Next'} />
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
                    <div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-4 sm:px-6 md:flex-row md:items-center">
                        <a
                            href="/"
                            className="shrink-0 rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>
                        <form className="flex min-w-0 flex-1 gap-2" action="/search" method="get" role="search">
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
                                    defaultValue={search.query}
                                    maxLength={80}
                                    autoFocus={!hasQuery}
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

                <main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-8 sm:px-6">
                    <div className="max-w-4xl">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Search</p>
                        <h1 className="mt-2 text-3xl font-semibold tracking-tight">Music knowledge results</h1>
                        <p className="mt-3 text-sm leading-6 text-slate-600">
                            Results come directly from canonical SongChart data. Entity type and disambiguation stay visible so equal names never become identity decisions.
                        </p>

                        {!hasQuery && (
                            <section className="mt-7 rounded-[0.875rem] border border-slate-300 bg-slate-50 p-6">
                                <h2 className="font-semibold">Start with a music name</h2>
                                <p className="mt-2 text-sm leading-6 text-slate-600">
                                    Search artists, releases or recordings. Dedicated fuzzy search and recommendations are not active.
                                </p>
                            </section>
                        )}

                        {hasQuery && search.items.length === 0 && (
                            <section aria-live="polite" className="mt-7 rounded-[0.875rem] border border-slate-300 bg-slate-50 p-6">
                                <h2 className="font-semibold">No results</h2>
                                <p className="mt-2 text-sm leading-6 text-slate-600">
                                    No canonical Artist, Release or Recording matched “{search.query}”. Unknown data is not replaced with guessed matches.
                                </p>
                            </section>
                        )}

                        {search.items.length > 0 && (
                            <section aria-label="Search results" className="mt-7">
                                <p className="mb-3 text-sm text-slate-600" aria-live="polite">
                                    {search.items.length} {search.items.length === 1 ? 'result' : 'results'} for “{search.query}”
                                </p>
                                <div className="divide-y divide-slate-200 border-y border-slate-300">
                                    {search.items.map((item) => (
                                        <article
                                            key={`${item.type}-${item.id}`}
                                            className="grid gap-1 py-4 sm:grid-cols-[7rem_minmax(0,1fr)] sm:gap-4"
                                        >
                                            <div className="text-xs font-semibold tracking-[0.08em] text-blue-700 uppercase">
                                                {item.type}
                                            </div>
                                            <div className="min-w-0">
                                                <h2 className="text-base font-semibold break-words">
                                                    <a
                                                        href={item.path}
                                                        className="rounded-sm text-blue-800 outline-none hover:underline focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                                    >
                                                        {item.name}
                                                    </a>
                                                </h2>
                                                <p className="mt-1 break-words text-sm leading-6 text-slate-600">{item.detail}</p>
                                            </div>
                                        </article>
                                    ))}
                                </div>
                            </section>
                        )}
                    </div>
                </main>
            </div>
        </>
    );
}
