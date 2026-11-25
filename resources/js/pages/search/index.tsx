import { EntityResultRow } from '@/components/public-entity';
import { PublicShell } from '@/components/public-shell';
import { Head } from '@inertiajs/react';

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
            <PublicShell query={search.query} autoFocus={!hasQuery}>

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
                                        <EntityResultRow key={`${item.type}-${item.id}`} item={item} />
                                    ))}
                                </div>
                            </section>
                        )}
                    </div>
                </main>
            </PublicShell>
        </>
    );
}
