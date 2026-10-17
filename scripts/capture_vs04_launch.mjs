import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const baseUrl = process.env.VS04_BASE_URL ?? 'http://127.0.0.1:8000';
const evidenceDir = resolve(process.env.VS04_EVIDENCE_DIR ?? 'artifacts/vs04-launch');
const evidenceSha = process.env.VS04_EVIDENCE_SHA ?? 'unknown';

const viewports = [
    { width: 390, height: 844, label: 'narrow' },
    { width: 1440, height: 1024, label: 'wide' },
];

const surfaces = [
    { label: 'about', path: '/about', expected: ['About SongChart Next', 'What SongChart Next is', 'Data quality'] },
    { label: 'privacy', path: '/privacy', expected: ['Privacy', 'Public browsing', 'External destinations', 'Support and corrections'] },
    { label: 'terms', path: '/terms', expected: ['Terms of use', 'Informational metadata', 'External services', 'Launch status'] },
    { label: 'disclaimer', path: '/disclaimer', expected: ['Disclaimer', 'Metadata can change', 'No media redistribution claim'] },
    { label: 'support', path: '/support', expected: ['Support', 'Keep secrets out of public issues', 'Open the SongChart issue tracker'] },
    {
        label: 'corrections',
        path: '/corrections',
        expected: [
            'Corrections',
            'Identify the canonical record',
            'A correction submission never writes canonical tables directly',
            'Submit correction evidence',
            'Submit for review',
            'Stored as submitted; SongChart does not fetch this URL during intake.',
        ],
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
const evidence = { schemaVersion: 1, sourceRevision: evidenceSha, browser: browserVersion, generatedAt: new Date().toISOString(), captures: [] };

for (const surface of surfaces) {
    const url = new URL(surface.path, baseUrl).toString();
    for (const viewport of viewports) {
        const stem = `${surface.label}--${viewport.width}x${viewport.height}`;
        const screenshotPath = resolve(evidenceDir, `${stem}.png`);
        const domPath = resolve(evidenceDir, `${stem}.html`);
        const args = ['--headless=new', '--no-sandbox', '--disable-gpu', '--force-device-scale-factor=1', `--window-size=${viewport.width},${viewport.height}`, '--virtual-time-budget=2500'];
        chrome(chromePath, [...args, `--screenshot=${screenshotPath}`, url]);
        const dom = chrome(chromePath, [...args, '--dump-dom', url]).stdout;
        writeFileSync(domPath, dom);

        for (const text of surface.expected) {
            if (!dom.includes(text)) throw new Error(`${surface.path} did not hydrate expected text: ${text}`);
        }
        for (const text of ['Skip to content', 'role="search"', 'aria-label="Site information"', 'About', 'Privacy', 'Terms', 'Disclaimer', 'Support', 'Corrections', 'Sitemap']) {
            if (!dom.includes(text)) throw new Error(`${surface.path} missing public-shell contract: ${text}`);
        }
        if (!dom.includes('name="description"')) throw new Error(`${surface.path} missing meta description.`);
        if (!dom.includes('rel="canonical"')) throw new Error(`${surface.path} missing canonical metadata.`);
        if (dom.includes('/@vite/client') || dom.includes('127.0.0.1:5173')) throw new Error(`${surface.path} unexpectedly references Vite dev server.`);

        if (surface.label === 'support') {
            if (!dom.includes('https://github.com/fusumivietnam/SongChart-Next/issues/new')) throw new Error(`${surface.path} missing issue-tracker action.`);
            if (!dom.includes('rel="noopener noreferrer"')) throw new Error(`${surface.path} missing external-link opener isolation.`);
            if (!dom.includes('referrerpolicy="no-referrer"')) throw new Error(`${surface.path} missing no-referrer treatment.`);
        }

        if (surface.label === 'corrections') {
            for (const text of ['id="subject-type"', 'id="subject-id"', 'id="claim"', 'id="evidence-url"']) {
                if (!dom.includes(text)) throw new Error(`${surface.path} missing correction-intake form contract: ${text}`);
            }
            if (dom.includes('https://github.com/fusumivietnam/SongChart-Next/issues/new')) throw new Error(`${surface.path} unexpectedly exposes the old issue-tracker correction action.`);
        }

        const dimensions = pngDimensions(screenshotPath);
        if (dimensions.width !== viewport.width || dimensions.height !== viewport.height) throw new Error(`${stem} was ${dimensions.width}x${dimensions.height}.`);
        evidence.captures.push({ surface: surface.label, route: surface.path, viewport, screenshot: `${stem}.png`, renderedDom: `${stem}.html` });
        process.stdout.write(`Verified ${surface.path} at ${viewport.width}x${viewport.height}\n`);
    }
}

writeFileSync(resolve(evidenceDir, 'evidence.json'), `${JSON.stringify(evidence, null, 2)}\n`);
