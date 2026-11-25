type EntityItem = { type: string; name: string; detail: string; path: string };

export function EntityResultRow({ item, discovery = false }: { item: EntityItem; discovery?: boolean }) {
    const Heading = discovery ? 'h3' : 'h2';
    return (
        <article className={discovery ? 'grid gap-1 py-4' : 'grid gap-1 py-4 sm:grid-cols-[7rem_minmax(0,1fr)] sm:gap-4'}>
            <div className="text-xs font-semibold tracking-[0.08em] text-blue-700 uppercase">{item.type}</div>
            <div className="min-w-0">
                <Heading className="text-base font-semibold break-words">
                    <a href={item.path} className="rounded-sm text-blue-800 outline-none hover:underline focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">{item.name}</a>
                </Heading>
                <p className="mt-1 break-words text-sm leading-6 text-slate-600">{item.detail}</p>
            </div>
        </article>
    );
}

export function MetadataRow({ label, value }: { label: string; value: string }) {
    return <div className="grid gap-1 border-t border-slate-200 py-3 text-sm first:border-t-0 sm:grid-cols-[7rem_minmax(0,1fr)] sm:gap-3"><dt className="font-medium text-slate-600">{label}</dt><dd className="min-w-0 break-words text-slate-900">{value}</dd></div>;
}

export function ArtworkPlaceholder({ name, recording = false }: { name: string; recording?: boolean }) {
    const label = recording ? 'Recording metadata' : 'Artwork unavailable';
    return <div role="img" aria-label={label + ' for ' + name} className="flex aspect-square w-full max-w-48 items-center justify-center rounded-[0.875rem] border border-slate-300 bg-slate-100 p-4 text-center text-sm font-medium text-slate-600 md:max-w-none">{label}</div>;
}
