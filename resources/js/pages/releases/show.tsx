import { ArtworkPlaceholder, MetadataRow } from '@/components/public-entity';
import { PublicShell } from '@/components/public-shell';
import { Head } from '@inertiajs/react';

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



function duration(ms: number | null) {
    if (ms === null) return 'Unknown';
    const total = Math.round(ms / 1000); return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}

export default function ReleaseShow({ release }: Props) {
    const creditLine = release.credits.length ? release.credits.map((c) => c.credited_as + c.join_phrase).join('') : 'Unknown';
    const source = release.provenance[0];
    return <><Head title={`${release.title} — SongChart Next`}/><PublicShell><main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-8 sm:px-6"><p className="mb-2 text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">Release</p><h1 className="max-w-4xl text-3xl leading-tight font-semibold tracking-tight break-words sm:text-4xl">{release.title}</h1><p className="mt-3 text-sm text-slate-600">{creditLine}</p><section className="mt-7 grid gap-6 md:grid-cols-[14rem_minmax(0,1fr)] md:items-start"><ArtworkPlaceholder name={release.title} /><div className="min-w-0"><dl className="rounded-[0.875rem] border border-slate-300 bg-white px-4"><MetadataRow label="Release group" value={release.releaseGroup ? `${release.releaseGroup.title}${release.releaseGroup.type ? ` · ${release.releaseGroup.type}` : ''}` : 'Unknown'}/><MetadataRow label="Date" value={release.date ?? 'Unknown'}/><MetadataRow label="Country" value={release.countryCode ?? 'Unknown'}/><MetadataRow label="Status" value={release.status ?? 'Unknown'}/><MetadataRow label="Barcode" value={release.barcode ?? 'Unknown'}/><MetadataRow label="SongChart ID" value={release.id}/><MetadataRow label="Provenance" value={source ? `${source.provider} · ${source.external_id}` : 'No external provenance recorded'}/></dl></div></section><section className="mt-8"><h2 className="text-lg font-semibold">Tracklist</h2><div className="mt-3 space-y-5">{release.media.map((medium) => <div key={medium.position} className="rounded-[0.875rem] border border-slate-300 bg-white"><div className="border-b border-slate-200 px-4 py-3 text-sm font-medium">Medium {medium.position}{medium.format ? ` · ${medium.format}` : ''}</div><ol className="divide-y divide-slate-200">{medium.tracks.map((track) => <li key={`${medium.position}-${track.position}`} className="grid grid-cols-[2.5rem_minmax(0,1fr)_4rem] gap-3 px-4 py-3 text-sm"><span className="text-slate-600">{track.number}</span><a href={`/recordings/${track.recording_id}/${track.recording_slug}`} className="min-w-0 break-words rounded-sm font-medium text-blue-700 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">{track.title}<span className="block text-xs font-normal text-slate-600">Recording: {track.recording_title}</span></a><span className="text-right text-slate-600">{duration(track.length_ms)}</span></li>)}</ol></div>)}</div></section><section className="mt-8 border-t border-slate-200 pt-5 text-sm text-slate-600"><h2 className="font-semibold text-slate-900">Identity and provenance</h2><p className="mt-2 leading-6">Release identity is separate from Release Group, Recording and provider identifiers. Track rows describe placement on this release and do not become canonical recordings.</p><a href={`/corrections?subject_type=release&subject_id=${release.id}`} className="mt-3 inline-block rounded-sm text-sm font-medium text-blue-700 underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">Report a correction</a></section></main>
                </PublicShell></>;
}
