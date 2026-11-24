const siteLinks = [
    { href: '/about', label: 'About' },
    { href: '/privacy', label: 'Privacy' },
    { href: '/terms', label: 'Terms' },
    { href: '/disclaimer', label: 'Disclaimer' },
    { href: '/support', label: 'Support' },
    { href: '/corrections', label: 'Corrections' },
    { href: '/sitemap.xml', label: 'Sitemap' },
] as const;

/** Public informational navigation; never imports authenticated starter UI. */
export function PublicFooter() {
    return (
        <footer className="mt-auto border-t border-slate-300 bg-slate-50 text-slate-700">
            <nav
                aria-label="Site information"
                className="mx-auto flex w-full max-w-[72rem] flex-wrap items-center gap-x-5 gap-y-3 px-4 py-6 text-sm sm:px-6"
            >
                {siteLinks.map(({ href, label }) => (
                    <a
                        key={href}
                        href={href}
                        className="rounded-sm underline-offset-4 hover:text-blue-800 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                    >
                        {label}
                    </a>
                ))}
            </nav>
        </footer>
    );
}
