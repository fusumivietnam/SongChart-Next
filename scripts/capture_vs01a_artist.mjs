import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const baseUrl = process.env.VS01A_BASE_URL ?? 'http://127.0.0.1:8000';
const artistPath = process.env.VS01A_ARTIST_PATH;
const evidenceDir = resolve(process.env.VS01A_EVIDENCE_DIR ?? 'artifacts/vs01a-artist');
const evidenceSha = process.env.VS01A_EVIDENCE_SHA ?? 'unknown';

if (!artistPath || !artistPath.startsWith('/artists/')) {
    throw new Error('VS01A_ARTIST_PATH must be a canonical /artists/... path.');
}

const viewports = [
    { width: 390, height: 844, label: 'narrow' },
    { width: 1440, height: 1024, label: 'wide' },
];

const expected = [
    'SongChart Next',
    'Aster Echo',
    'Artwork unavailable',
    '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
    'name-only match',
];

function findChrome() {
    const result = spawnSync(
        'bash',
        ['-lc', 'command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser'],
        { encoding: 'utf8' },
    );

    if (result.status !== 0 || !result.stdout.trim()) {
        throw new Error('No supported Chrome/Chromium executable found.');
    }

    return result.stdout.trim().split('\n')[0];
}

function chrome(chromePath, args) {
    const result = spawnSync(chromePath, args, {
        encoding: 'utf8',
        maxBuffer: 16 * 1024 * 1024,
    });

    if (result.status !== 0) {
        throw new Error([`Chrome exited with status ${result.status}`, result.stdout, result.stderr].filter(Boolean).join('\n'));
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
const browserVersion = spawnSync(chromePath, ['--version'], { encoding: 'utf8' }).stdout.trim();
const url = new URL(artistPath, baseUrl).toString();
const evidence = {
    schemaVersion: 1,
    sourceRevision: evidenceSha,
    route: artistPath,
    browser: browserVersion,
    generatedAt: new Date().toISOString(),
    captures: [],
};

for (const viewport of viewports) {
    const stem = `artist--${viewport.width}x${viewport.height}`;
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

    chrome(chromePath, [...commonArgs, `--screenshot=${screenshotPath}`, url]);
    const dom = chrome(chromePath, [...commonArgs, '--dump-dom', url]).stdout;
    writeFileSync(domPath, dom);

    for (const text of expected) {
        if (!dom.includes(text)) {
            throw new Error(`Public Artist page did not hydrate expected text: ${text}`);
        }
    }

    if (dom.includes('/@vite/client') || dom.includes('127.0.0.1:5173') || dom.includes('0.0.0.0:5173')) {
        throw new Error('Public Artist page unexpectedly references the Vite development server.');
    }

    const dimensions = pngDimensions(screenshotPath);
    if (dimensions.width !== viewport.width || dimensions.height !== viewport.height) {
        throw new Error(`${stem} was ${dimensions.width}x${dimensions.height}; expected ${viewport.width}x${viewport.height}.`);
    }

    evidence.captures.push({ viewport, screenshot: `${stem}.png`, renderedDom: `${stem}.html` });
    process.stdout.write(`Verified ${artistPath} at ${viewport.width}x${viewport.height}\n`);
}

writeFileSync(resolve(evidenceDir, 'evidence.json'), `${JSON.stringify(evidence, null, 2)}\n`);
