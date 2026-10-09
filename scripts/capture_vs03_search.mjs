import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const baseUrl = process.env.VS03_BASE_URL ?? 'http://127.0.0.1:8000';
const evidenceDir = resolve(process.env.VS03_EVIDENCE_DIR ?? 'artifacts/vs03-search');
const evidenceSha = process.env.VS03_EVIDENCE_SHA ?? 'unknown';
const artistPath = process.env.VS03_ARTIST_PATH;
const releasePath = process.env.VS03_RELEASE_PATH;
const recordingPath = process.env.VS03_RECORDING_PATH;
const destinationUrl = 'https://listen.example.test/recordings/signals-at-dawn';

for (const [name, path, prefix] of [
    ['VS03_ARTIST_PATH', artistPath, '/artists/'],
    ['VS03_RELEASE_PATH', releasePath, '/releases/'],
    ['VS03_RECORDING_PATH', recordingPath, '/recordings/'],
]) {
    if (!path?.startsWith(prefix)) throw new Error(`${name} must be a canonical ${prefix} path.`);
}

const viewports = [
    { width: 390, height: 844, label: 'narrow' },
    { width: 1440, height: 1024, label: 'wide' },
];

const surfaces = [
    {
        label: 'results',
        path: '/search?q=Aster%20Echo',
        expected: ['SongChart Next', 'Music knowledge results', 'Aster Echo', 'Artist'],
        expectedLinks: [artistPath],
    },
    {
        label: 'artist',
        path: artistPath,
        expected: ['SongChart Next', 'Aster Echo', 'Releases and relationships', 'Signals at Dawn', '2024'],
        expectedLinks: [releasePath],
    },
    {
        label: 'release',
        path: releasePath,
        expected: ['SongChart Next', 'Signals at Dawn', 'Tracklist', 'Recording: Signals at Dawn'],
        expectedLinks: [recordingPath],
    },
    {
        label: 'recording',
        path: recordingPath,
        expected: ['SongChart Next', 'Signals at Dawn', 'Works', 'Appears on releases', 'Listen or watch elsewhere', 'Fixture Audio', 'Open external destination'],
        expectedLinks: [releasePath, destinationUrl],
    },
    {
        label: 'empty',
        path: '/search?q=definitely-not-canonical',
        expected: ['SongChart Next', 'Music knowledge results', 'No results', 'Unknown data is not replaced with guessed matches'],
        expectedLinks: [],
    },
];

function findChrome() {
    const result = spawnSync('bash', ['-lc', 'command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser'], { encoding: 'utf8' });
    if (result.status !== 0 || !result.stdout.trim()) throw new Error('No supported Chrome/Chromium executable found.');
    return result.stdout.trim().split('\n')[0];
}

function chrome(chromePath, args) {
    const result = spawnSync(chromePath, args, { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
    if (result.status !== 0) throw new Error([`Chrome exited with status ${result.status}`, result.stdout, result.stderr].filter(Boolean).join('\n'));
    return result;
}

function pngDimensions(path) {
    const png = readFileSync(path);
    if (png.toString('ascii', 1, 4) !== 'PNG') throw new Error(`Expected PNG screenshot at ${path}`);
    return { width: png.readUInt32BE(16), height: png.readUInt32BE(20) };
}

mkdirSync(evidenceDir, { recursive: true });
const chromePath = findChrome();
const browserVersion = spawnSync(chromePath, ['--version'], { encoding: 'utf8' }).stdout.trim();
const evidence = { schemaVersion: 3, sourceRevision: evidenceSha, browser: browserVersion, generatedAt: new Date().toISOString(), journey: [artistPath, releasePath, recordingPath, destinationUrl], captures: [] };

for (const surface of surfaces) {
    const url = new URL(surface.path, baseUrl).toString();
    for (const viewport of viewports) {
        const stem = `${surface.label}--${viewport.width}x${viewport.height}`;
        const screenshotPath = resolve(evidenceDir, `${stem}.png`);
        const domPath = resolve(evidenceDir, `${stem}.html`);
        const args = ['--headless=new', '--no-sandbox', '--disable-gpu', '--force-device-scale-factor=1', `--window-size=${viewport.width},${viewport.height}`, '--virtual-time-budget=3000'];
        chrome(chromePath, [...args, `--screenshot=${screenshotPath}`, url]);
        const dom = chrome(chromePath, [...args, '--dump-dom', url]).stdout;
        writeFileSync(domPath, dom);

        for (const text of surface.expected) {
            if (!dom.includes(text)) throw new Error(`${surface.label} did not hydrate expected text: ${text}`);
        }
        for (const path of surface.expectedLinks) {
            if (!dom.includes(`href="${path}"`)) throw new Error(`${surface.label} is missing journey link: ${path}`);
        }
        if (surface.label === 'recording') {
            if (!dom.includes('target="_blank"')) throw new Error('Recording destination is missing explicit external target treatment.');
            if (!dom.includes('rel="noopener noreferrer"')) throw new Error('Recording destination is missing opener isolation.');
        }
        if (!dom.includes('role="search"')) throw new Error(`${surface.label} is missing the search landmark.`);
        if (!dom.includes('Skip to content')) throw new Error(`${surface.label} is missing the skip link.`);
        if (dom.includes('/@vite/client') || dom.includes('127.0.0.1:5173')) throw new Error(`${surface.label} unexpectedly references Vite dev server.`);

        const dimensions = pngDimensions(screenshotPath);
        if (dimensions.width !== viewport.width || dimensions.height !== viewport.height) throw new Error(`${stem} was ${dimensions.width}x${dimensions.height}.`);
        evidence.captures.push({ surface: surface.label, route: surface.path, viewport, screenshot: `${stem}.png`, renderedDom: `${stem}.html` });
        process.stdout.write(`Verified ${surface.path} at ${viewport.width}x${viewport.height}\n`);
    }
}

writeFileSync(resolve(evidenceDir, 'evidence.json'), `${JSON.stringify(evidence, null, 2)}\n`);
