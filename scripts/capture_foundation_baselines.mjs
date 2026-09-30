import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const baseUrl = process.env.FOUNDATION_BASE_URL ?? 'http://127.0.0.1:8000';
const evidenceDir = resolve(process.env.FOUNDATION_EVIDENCE_DIR ?? 'artifacts/foundation-baselines');
const evidenceSha = process.env.FOUNDATION_EVIDENCE_SHA ?? 'unknown';

const surfaces = [
    {
        name: 'artist',
        path: '/_design/foundation/artist',
        expected: [
            'SongChart Next',
            'Aster Echo',
            'Artwork unavailable',
            'Deterministic design fixture — not canonical data',
        ],
    },
    {
        name: 'artist-long',
        path: '/_design/foundation/artist-long',
        expected: [
            'SongChart Next',
            '青い海 Orchestra — Ensemble for Transcontinental Night Sessions',
            'Artwork unavailable',
        ],
    },
    {
        name: 'search',
        path: '/_design/foundation/search',
        expected: [
            'Music knowledge results',
            'Signals at Dawn',
            'Recording · 4:12 · deterministic fixture',
        ],
    },
    {
        name: 'search-empty',
        path: '/_design/foundation/search-empty',
        expected: [
            'No results',
            'Unknown data is not replaced with guessed matches.',
        ],
    },
    {
        name: 'search-error',
        path: '/_design/foundation/search-error',
        expected: [
            'Search could not be completed',
            'Retry search',
        ],
    },
];

const viewports = [
    { width: 390, height: 844, label: 'narrow' },
    { width: 1440, height: 1024, label: 'wide' },
];

function findChrome() {
    const result = spawnSync(
        'bash',
        [
            '-lc',
            'command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser',
        ],
        { encoding: 'utf8' },
    );

    if (result.status !== 0 || !result.stdout.trim()) {
        throw new Error(
            'No supported Chrome/Chromium executable found on the GitHub runner.',
        );
    }

    return result.stdout.trim().split('\n')[0];
}

function chrome(chromePath, args, options = {}) {
    const result = spawnSync(chromePath, args, {
        encoding: options.encoding ?? 'utf8',
        maxBuffer: 16 * 1024 * 1024,
    });

    if (result.status !== 0) {
        throw new Error(
            [
                `Chrome exited with status ${result.status}`,
                result.stdout || '',
                result.stderr || '',
            ]
                .filter(Boolean)
                .join('\n'),
        );
    }

    return result;
}

function pngDimensions(path) {
    const png = readFileSync(path);

    if (png.toString('ascii', 1, 4) !== 'PNG') {
        throw new Error(`Expected PNG screenshot at ${path}`);
    }

    return {
        width: png.readUInt32BE(16),
        height: png.readUInt32BE(20),
    };
}

mkdirSync(evidenceDir, { recursive: true });

const chromePath = findChrome();
const browserVersion = execFileSync(chromePath, ['--version'], {
    encoding: 'utf8',
}).trim();

const evidence = {
    schemaVersion: 1,
    sourceRevision: evidenceSha,
    baseUrl,
    browser: browserVersion,
    generatedAt: new Date().toISOString(),
    note: 'Automated render evidence only. Human Design Authority approval remains required.',
    captures: [],
};

for (const surface of surfaces) {
    const url = new URL(surface.path, baseUrl).toString();

    for (const viewport of viewports) {
        const stem = `${surface.name}--${viewport.width}x${viewport.height}`;
        const screenshotPath = resolve(evidenceDir, `${stem}.png`);
        const domPath = resolve(evidenceDir, `${stem}.html`);

        const commonArgs = [
            '--headless=new',
            '--no-sandbox',
            '--disable-gpu',
            '--force-device-scale-factor=1',
            `--window-size=${viewport.width},${viewport.height}`,
            '--virtual-time-budget=3000',
        ];

        chrome(chromePath, [
            ...commonArgs,
            `--screenshot=${screenshotPath}`,
            url,
        ]);

        const dom = chrome(chromePath, [
            ...commonArgs,
            '--dump-dom',
            url,
        ]).stdout;

        writeFileSync(domPath, dom);

        for (const expected of surface.expected) {
            if (!dom.includes(expected)) {
                throw new Error(
                    `${surface.path} did not hydrate expected fixture text: ${expected}`,
                );
            }
        }

        if (
            dom.includes('0.0.0.0:5173') ||
            dom.includes('127.0.0.1:5173') ||
            dom.includes('/@vite/client')
        ) {
            throw new Error(
                `${surface.path} unexpectedly references the Vite development server.`,
            );
        }

        const dimensions = pngDimensions(screenshotPath);

        if (
            dimensions.width !== viewport.width ||
            dimensions.height !== viewport.height
        ) {
            throw new Error(
                `${stem} screenshot dimensions were ${dimensions.width}x${dimensions.height}; expected ${viewport.width}x${viewport.height}.`,
            );
        }

        evidence.captures.push({
            surface: surface.name,
            route: surface.path,
            viewport,
            screenshot: `${stem}.png`,
            renderedDom: `${stem}.html`,
            fixtureAssertions: surface.expected,
        });

        process.stdout.write(
            `Verified ${surface.path} at ${viewport.width}x${viewport.height}\n`,
        );
    }
}

writeFileSync(
    resolve(evidenceDir, 'evidence.json'),
    `${JSON.stringify(evidence, null, 2)}\n`,
);

process.stdout.write(
    `Captured ${evidence.captures.length} deterministic Foundation references with ${browserVersion}.\n`,
);
