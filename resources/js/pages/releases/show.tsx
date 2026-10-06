import { Head } from '@inertiajs/react';
import { Search } from 'lucide-react';

type Credit = { artist_id: string; artist_slug: string; name: string; role: string; credited_as: string; join_phrase: string; position: number };
type Track = { position: number; number: string; title: string; length_ms: number | null; recording_id: string; recording_slug: string; recording_title: string };
type Medium = { position: number; format: string | null; title: string | null; tracks: Track[] };
type Provenance = { provider: string; entity_type: string; external_id: string; source_name: string };
type Release = {
    id: string; slug: string; title: string; status: string | null; countryCode: string | null;
    date: string | null; datePrecision: string | null; barcode: string | null;
    releaseGroup: { id: string; title: string; type: string | null } | null;
    credits: Credit[]; media: Medium[]; provenance: Provenance[];
};
type Props = { release: Release };

function Header() {
    return <header className="border-b border-slate-300 bg-white"><div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-4 sm:px-6 md:flex-row md:items-center"><a href="/" className="shrink-0 rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">SongChart Next</a><form className="flex min-w-0 flex-1 gap-2" action="/" method="get" role="search"><label htmlFor="site-search" className="sr-only">Search music knowledge</label><div className="relative min-w-0 flex-1"><Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-500"/><input id="site-search" name="q" placeholder="Search artists, releases, recordings" className="h-10 w-full rounded-[0.625rem] border border-slate-300 bg-white pr-3 pl-9 text-sm outline-none placeholder:text-slate-500 focus-visible:border-blue-700 focus-visible:ring-2 focus-visible:ring-blue-600/25"/></div><button type="submit" className="h-10 rounded-[0.625rem] bg-blue-700 px-4 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">Search</button></form></div></header>;
}

function Meta({ label, value }: { label: string; value: string }) {
    return <div className="grid grid-cols-[7rem_1fr] gap-3 border-t border-slate-200 py-3 text-sm first:border-t-0"><dt className="font-medium text-slate-600">{label}</dt><dd className="min-w-0 break-words text-slate-900">{value}</dd></div>;
}

function duration(ms: number | null) {
    if (ms === null) return 'Unknown';
    const total = Math.round(ms / 1000); return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}

export default function ReleaseShow({ release }: Props) {
    const creditLine = release.credits.length ? release.credits.map((c) => c.credited_as + c.join_phrase).join('') : 'Unknown';
    const source = release.provenance[0];
    return <><Head title={`${release.title} — SongChart Next`}/><div className="min-h-screen bg-white text-slate-900" style={{fontFamily:'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'}}><a href="#main-content" className="sr-only rounded-md bg-blue-700 px-3 py-2 text-white focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50">Skip to content</a><Header/><main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-8 sm:px-6"><p className="mb-2 text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Release</p><h1 className="max-w-4xl text-3xl leading-tight font-semibold tracking-tight break-words sm:text-4xl">{release.title}</h1><p className="mt-3 text-sm text-slate-600">{creditLine}</p><section className="mt-7 grid gap-6 md:grid-cols-[14rem_minmax(0,1fr)] md:items-start"><div role="img" aria-label={`Artwork unavailable for ${release.title}`} className="flex aspect-square items-center justify-center rounded-[0.875rem] border border-slate-300 bg-slate-100 p-4 text-center text-sm font-medium text-slate-500">Artwork unavailable</div><div className="min-w-0"><dl className="rounded-[0.875rem] border border-slate-300 bg-white px-4"><Meta label="Release group" value={release.releaseGroup ? `${release.releaseGroup.title}${release.releaseGroup.type ? ` · ${release.releaseGroup.type}` : ''}` : 'Unknown'}/><Meta label="Date" value={release.date ?? 'Unknown'}/><Meta label="Country" value={release.countryCode ?? 'Unknown'}/><Meta label="Status" value={release.status ?? 'Unknown'}/><Meta label="Barcode" value={release.barcode ?? 'Unknown'}/><Meta label="SongChart ID" value={release.id}/><Meta label="Provenance" value={source ? `${source.provider} · ${source.external_id}` : 'No external provenance recorded'}/></dl></div></section><section className="mt-8"><h2 className="text-lg font-semibold">Tracklist</h2><div className="mt-3 space-y-5">{release.media.map((medium) => <div key={medium.position} className="rounded-[0.875rem] border border-slate-300 bg-white"><div className="border-b border-slate-200 px-4 py-3 text-sm font-medium">Medium {medium.position}{medium.format ? ` · ${medium.format}` : ''}</div><ol className="divide-y divide-slate-200">{medium.tracks.map((track) => <li key={`${medium.position}-${track.position}`} className="grid grid-cols-[2.5rem_minmax(0,1fr)_4rem] gap-3 px-4 py-3 text-sm"><span className="text-slate-500">{track.number}</span><a href={`/recordings/${track.recording_id}/${track.recording_slug}`} className="min-w-0 font-medium text-blue-700 hover:underline">{track.title}<span className="block text-xs font-normal text-slate-500">Recording: {track.recording_title}</span></a><span className="text-right text-slate-500">{duration(track.length_ms)}</span></li>)}</ol></div>)}</div></section><section className="mt-8 border-t border-slate-200 pt-5 text-sm text-slate-600"><h2 className="font-semibold text-slate-900">Identity and provenance</h2><p className="mt-2 leading-6">Release identity is separate from Release Group, Recording and provider identifiers. Track rows describe placement on this release and do not become canonical recordings.</p></section></main></div></>;
}
