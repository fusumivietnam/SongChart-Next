#!/usr/bin/env python3
"""Generate a read-only Foundation dependency/runtime provenance report from repository authorities."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "Dockerfile"
COMPOSE = ROOT / "compose.yaml"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else "unknown"

def dockerfile_images():
    images = []
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^FROM\s+([^\s]+)(?:\s+AS\s+([\w-]+))?", line, re.I)
        if not m:
            continue
        image, stage = m.groups()
        # Internal stage references have no registry/tag separator and match earlier AS names.
        if ":" in image or "@" in image or "/" in image:
            images.append({"reference": image, "stage": stage})
    return images

def compose_postgres():
    text = COMPOSE.read_text(encoding="utf-8")
    m = re.search(r"^\s*image:\s*(postgres:[^\s#]+)", text, re.M)
    return m.group(1) if m else None

def parse_composer():
    lock = json.loads((ROOT / "composer.lock").read_text(encoding="utf-8"))
    wanted = {"laravel/framework", "inertiajs/inertia-laravel", "laravel/fortify"}
    packages = {}
    for p in lock.get("packages", []) + lock.get("packages-dev", []):
        if p["name"] in wanted:
            packages[p["name"]] = p["version"]
    return {"content_hash": lock.get("content-hash"), "selected": packages}

def parse_pnpm():
    text = (ROOT / "pnpm-lock.yaml").read_text(encoding="utf-8")
    wanted = ["@inertiajs/react", "react", "react-dom", "typescript", "vite", "tailwindcss"]
    selected = {}
    for name in wanted:
        # Resolve the importer entry without needing a YAML dependency.
        block = re.search(rf"(?m)^\s{{6}}{re.escape(name)}:\n\s{{8}}specifier:[^\n]+\n\s{{8}}version:\s*([^\n]+)", text)
        if block:
            selected[name] = block.group(1).strip()
    return {"lockfile_version": (re.search(r"^lockfileVersion:\s*['\"]?([^'\"\n]+)", text, re.M) or [None, None])[1], "selected": selected}

def starter_revision():
    path = ROOT / "docs" / "engineering" / "UPSTREAM_STARTER.md"
    if not path.exists():
        return None
    m = re.search(r"([0-9a-f]{40})", path.read_text(encoding="utf-8"))
    return m.group(1) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-digests", help="JSON file mapping image references to resolved manifest digests")
    ap.add_argument("--list-images", action="store_true", help="Print external container image references and exit")
    ap.add_argument("--require-digests", action="store_true", help="Fail unless every external image resolved to a sha256 digest")
    ap.add_argument("--output", help="Write report JSON to path")
    args = ap.parse_args()
    refs = []
    for item in dockerfile_images():
        if item["reference"] not in refs:
            refs.append(item["reference"])
    pg = compose_postgres()
    if pg and pg not in refs:
        refs.append(pg)
    if args.list_images:
        print("\n".join(refs))
        return

    digests = {}
    if args.image_digests:
        digests = json.loads(Path(args.image_digests).read_text(encoding="utf-8"))
    if args.require_digests:
        missing = [ref for ref in refs if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(digests.get(ref, "")))]
        if missing:
            raise SystemExit("Missing/invalid resolved image digests: " + ", ".join(missing))

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "fusumivietnam/SongChart-Next",
        "commit": git("rev-parse", "HEAD"),
        "starter": {
            "source": "https://github.com/laravel/react-starter-kit",
            "revision": starter_revision(),
        },
        "lockfiles": {
            "composer.lock": {"sha256": sha256(ROOT / "composer.lock"), **parse_composer()},
            "pnpm-lock.yaml": {"sha256": sha256(ROOT / "pnpm-lock.yaml"), **parse_pnpm()},
        },
        "container_images": [
            {"reference": ref, "resolved_digest": digests.get(ref), "immutable": "@sha256:" in ref}
            for ref in refs
        ],
        "policy": {
            "local_tags_permitted": True,
            "controlled_release_requires_digest_pin": True,
            "note": "Resolved digests are CI evidence for this run, not automatically approved production pins.",
        },
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")

if __name__ == "__main__":
    main()
