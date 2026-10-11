import { Head } from '@inertiajs/react';
import { ExternalLink, Search } from 'lucide-react';

type Section = {
    heading: string;
    paragraphs: string[];
};

type DocumentAction = {
    label: string;
    url: string;
};

type Props = {
    document: {
        slug: string;
        title: string;
        description: string;
        canonicalUrl: string;
        sections: Section[];
        action: DocumentAction | null;
    };
};

export default function SiteDocument({ document }: Props) {
    return (
        <>
            <Head title={`${document.title} — SongChart Next`}>
                <meta name="description" content={document.description} />
                <link rel="canonical" href={document.canonicalUrl} />
            </Head>
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
                    <div className="mx-auto flex max-w-[72rem] flex-col gap-4 px-4 py-4 sm:px-6 md:flex-row md:items-center md:justify-between">
                        <a
                            href="/"
                            className="w-fit rounded-md text-lg font-semibold tracking-tight outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                        >
                            SongChart Next
                        </a>
                        <form className="flex w-full max-w-md gap-2" action="/search" method="get" role="search">
                            <label htmlFor="site-search" className="sr-only">
                                Search music knowledge
                            </label>
                            <div className="relative min-w-0 flex-1">
                                <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-500" />
                                <input
                                    id="site-search"
                                    name="q"
                                    maxLength={80}
                                    placeholder="Search music knowledge"
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

                <main id="main-content" className="mx-auto w-full max-w-[72rem] px-4 py-10 sm:px-6">
                    <article className="max-w-3xl" aria-labelledby="document-title">
                        <p className="text-xs font-semibold tracking-[0.14em] text-blue-700 uppercase">SongChart Next</p>
                        <h1 id="document-title" className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                            {document.title}
                        </h1>
                        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">{document.description}</p>

                        <div className="mt-10 space-y-9">
                            {document.sections.map((section) => (
                                <section key={section.heading} className="border-t border-slate-300 pt-6">
                                    <h2 className="text-xl font-semibold tracking-tight">{section.heading}</h2>
                                    <div className="mt-3 space-y-3 text-[0.975rem] leading-7 text-slate-700">
                                        {section.paragraphs.map((paragraph) => (
                                            <p key={paragraph}>{paragraph}</p>
                                        ))}
                                    </div>
                                </section>
                            ))}
                        </div>

                        {document.action && (
                            <div className="mt-10 border-t border-slate-300 pt-6">
                                <a
                                    href={document.action.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    referrerPolicy="no-referrer"
                                    className="inline-flex items-center gap-2 rounded-[0.625rem] bg-blue-700 px-4 py-2.5 text-sm font-medium text-white outline-none hover:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                                >
                                    {document.action.label}
                                    <ExternalLink aria-hidden="true" className="h-4 w-4" />
                                </a>
                            </div>
                        )}
                    </article>
                </main>
            </div>
        </>
    );
}
