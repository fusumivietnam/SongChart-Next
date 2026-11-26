import { PublicFooter } from '@/components/public-footer';
import { Search } from 'lucide-react';
import type { ReactNode } from 'react';

type SearchProps = { id?: string; query?: string; hero?: boolean; autoFocus?: boolean };

export function GlobalSearch({ id = 'site-search', query = '', hero = false, autoFocus = false }: SearchProps) {
    return (
        <form className={hero ? 'mt-6 flex w-full max-w-2xl gap-2' : 'flex w-full min-w-0 gap-2 md:max-w-md'} action="/search" method="get" role="search">
            <label htmlFor={id} className="sr-only">Search artists, releases and recordings</label>
            <div className="relative min-w-0 flex-1">
                <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-600" />
                <input id={id} name="q" defaultValue={query} maxLength={80} autoFocus={autoFocus} placeholder="Search music" className="h-11 w-full rounded-[0.625rem] border border-slate-300 bg-white pr-3 pl-9 text-sm text-slate-900 outline-none placeholder:text-slate-600 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2" />
            </div>
            <button type="submit" className="h-11 shrink-0 rounded-[0.625rem] bg-blue-700 px-4 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">Search</button>
        </form>
    );
}

export function PublicShell({ children, home = false, query = '', autoFocus = false }: { children: ReactNode; home?: boolean; query?: string; autoFocus?: boolean }) {
    return (
        <div data-public-shell="true" className="flex min-h-screen flex-col bg-white text-slate-900" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
            <a href="#main-content" className="sr-only rounded-md bg-blue-700 px-3 py-2 text-white focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50">Skip to content</a>
            <header className="border-b border-slate-300 bg-white">
                <div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-3 sm:px-6 md:flex-row md:items-center md:justify-between">
                    <a href="/" className="inline-flex min-h-11 w-fit shrink-0 items-center rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2">SongChart Next</a>
                    {!home && <GlobalSearch query={query} autoFocus={autoFocus} />}
                </div>
            </header>
            {children}
            <PublicFooter />
        </div>
    );
}
