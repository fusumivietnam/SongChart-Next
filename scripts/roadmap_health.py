#!/usr/bin/env python3
"""Read-only roadmap controller: derive health/gaps from authored authorities + optional live GitHub."""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance"
ROADMAP = ROOT / "docs" / "roadmap" / "VERTICAL_SLICES.md"
LIFECYCLE_ORDER = {"candidate": 0, "approved": 1, "implemented": 2, "verified": 3, "deployed": 4, "watch": -1}
SLICE_RE = re.compile(r"^##\s+(FOUNDATION|VS-[0-9]+[a-z]?|Later(?:\s*/\s*activated only)?)\b", re.I)
BODY_SLICE_RE = re.compile(r"\*\*Slice ID:\*\*\s*([^\n]+)", re.I)
BODY_CAP_RE = re.compile(r"\*\*Capability ID\(s\):\*\*\s*([^\n]+)", re.I)\nBODY_BLOCKED_BY_RE = re.compile(r"\*\*Blocked by:\*\*\s*([^\n]*)", re.I)\nPR_ISSUE_RE = re.compile(r"(?:(?:implements|closes|fixes|resolves)\s+#(\d+)|Owning Issue / slice / capability:\s*#?(\d+))", re.I)
PR_OWNER_RE = re.compile(r"(?:Owning Issue / slice / capability|Slice ID):\s*([^\n]+)", re.I)
TITLE_SLICE_RE = re.compile(r"^\[?(FOUNDATION|VS-[0-9]+[a-z]?)\]?[\s:]+" , re.I)

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else None

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def parse_slices():
    slices = []
    for line in ROADMAP.read_text(encoding="utf-8").splitlines():
        m = SLICE_RE.match(line)
        if not m:
            continue
        raw = m.group(1)
        sid = "LATER" if raw.lower().startswith("later") else raw.upper()
        if sid not in slices:
            slices.append(sid)
    return slices

def normalize_slice(value):
    if not value:
        return None
    value = value.strip().upper()
    if value.startswith("LATER"):
        return "LATER"
    m = re.search(r"(FOUNDATION|VS-[0-9]+[A-Z]?)", value)
    return m.group(1) if m else None

def issue_slice(issue):
    body = issue.get("body") or ""
    m = BODY_SLICE_RE.search(body)
    if m:
        return normalize_slice(m.group(1))
    m = TITLE_SLICE_RE.match(issue.get("title") or "")
    return normalize_slice(m.group(1)) if m else None

def issue_capabilities(issue, known):
    body = issue.get("body") or ""
    m = BODY_CAP_RE.search(body)
    if not m:
        return []
    return sorted({cid for cid in re.findall(r"[a-z0-9][a-z0-9-]+", m.group(1).lower()) if cid in known})

def issue_blockers(issue):
    body = issue.get("body") or ""
    m = BODY_BLOCKED_BY_RE.search(body)
    if not m:
        return []
    value = m.group(1).strip()
    if not value or value.lower() in {"none", "n/a", "-"}:
        return []
    return sorted({int(n) for n in re.findall(r"#(\d+)", value)})

def pr_issue_numbers(pr):
    body = pr.get("body") or ""
    found = set()
    for m in PR_ISSUE_RE.finditer(body):
        for value in m.groups():
            if value:
                found.add(int(value))
    return sorted(found)

def api_get(repo, path, token):
    url = f"https://api.github.com/repos/{repo}{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "songchart-roadmap-controller",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def fetch_live(repo, token):
    if not token:
        return {"status": "unknown", "reason": "no GitHub token supplied", "issues": [], "pull_requests": []}
    try:
        # For project scale today a single 100-item page is sufficient. Report truncation instead of hiding it.
        raw_issues = api_get(repo, "/issues?state=all&per_page=100&sort=updated&direction=desc", token)
        issues = [x for x in raw_issues if "pull_request" not in x]
        pulls = api_get(repo, "/pulls?state=all&per_page=100&sort=updated&direction=desc", token)
        return {
            "status": "known",
            "truncated": len(raw_issues) == 100 or len(pulls) == 100,
            "issues": issues,
            "pull_requests": pulls,
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "unknown", "reason": f"GitHub query failed: {type(exc).__name__}", "issues": [], "pull_requests": []}

def finding(code, severity, message, **refs):
    return {"code": code, "severity": severity, "message": message, "refs": refs}

def derive(live):
    cmap = load_json(GOV / "CAPABILITY_MAP.json")
    triggers = load_json(GOV / "ACTIVATION_TRIGGERS.json")
    technologies = load_json(GOV / "TECHNOLOGY_REGISTRY.json")
    research = load_json(GOV / "RESEARCH_REGISTRY.json")
    slices = parse_slices()
    caps = {c["id"]: c for c in cmap["capabilities"]}
    findings = []
    execution = {sid: {"open_issues": [], "closed_issues": [], "open_prs": []} for sid in slices}
    issue_by_number = {}
    prs_by_issue = {}

    if "FOUNDATION" not in slices or "VS-01A" not in slices:
        findings.append(finding("roadmap.missing_core_slice", "error", "Expected FOUNDATION and VS-01a slices are not both declared."))

    if live["status"] == "unknown":
        findings.append(finding("live.unknown", "warning", live.get("reason", "live GitHub state unavailable")))
    else:
        if live.get("truncated"):
            findings.append(finding("live.truncated", "warning", "GitHub query reached 100-item page limit; report may be incomplete."))
        issue_by_number = {int(issue["number"]): issue for issue in live["issues"]}
        for issue in live["issues"]:
            sid = issue_slice(issue)
            if sid and sid in execution:
                key = "closed_issues" if issue.get("state") == "closed" else "open_issues"
                execution[sid][key].append({"number": issue["number"], "title": issue["title"], "url": issue["html_url"], "blockers": issue_blockers(issue)})
                referenced_caps = issue_capabilities(issue, caps)
                if not referenced_caps:
                    findings.append(finding("issue.missing_capability_link", "warning",
                        f"Issue #{issue['number']} is linked to {sid} but has no recognized Capability ID(s).",
                        issue=issue["number"], slice=sid))
            elif issue.get("state") == "open":
                findings.append(finding("issue.unlinked_open", "info",
                    f"Open Issue #{issue['number']} is not linked to a roadmap slice; acceptable for research/governance work if intentional.",
                    issue=issue["number"]))
        for pr in live["pull_requests"]:
            if pr.get("state") != "open":
                continue
            linked_issues = pr_issue_numbers(pr)
            for issue_number in linked_issues:
                prs_by_issue.setdefault(issue_number, []).append(pr)
            title_match = TITLE_SLICE_RE.match(pr.get("title") or "")
            sid = normalize_slice(title_match.group(1)) if title_match else None
            if not sid:
                owner_match = PR_OWNER_RE.search(pr.get("body") or "")
                sid = normalize_slice(owner_match.group(1)) if owner_match else None
            if sid in execution:
                execution[sid]["open_prs"].append({"number": pr["number"], "title": pr["title"], "url": pr["html_url"], "draft": pr.get("draft", False), "issue_numbers": linked_issues})

    # Capability lifecycle consistency / next-gate hints.
    for cid, cap in caps.items():
        status = cap["status"]
        if status in {"implemented", "verified", "deployed"} and not cap.get("implementation"):
            findings.append(finding("capability.missing_implementation", "error",
                f"{cid} is {status} but has no implementation reference.", capability=cid))
        if status in {"verified", "deployed"} and not cap.get("verification_evidence"):
            findings.append(finding("capability.missing_verification_evidence", "error",
                f"{cid} is {status} but has no verification evidence.", capability=cid))
        if status == "deployed" and not cap.get("deployment_evidence"):
            findings.append(finding("capability.missing_deployment_evidence", "error",
                f"{cid} is deployed but has no deployment evidence.", capability=cid))

    # Accepted research must have a decision reference; validator also enforces this, health report makes it visible.
    for item in research["research"]:
        if item["status"] == "accepted" and not item.get("decision_ref"):
            findings.append(finding("research.accepted_without_decision", "error",
                f"{item['id']} is accepted without decision reference.", research=item["id"]))

    # Ready/blocked is intentionally conservative: active execution can be shown, but capability promotion is never inferred.
    active = []
    blocked = []
    for sid, state in execution.items():
        if state["open_prs"] or state["open_issues"]:
            active.append({"slice": sid, **state})
    # Foundation gates later product slices until foundation work is explicitly completed by repository decisions.
    foundation_open = bool(execution.get("FOUNDATION", {}).get("open_issues") or execution.get("FOUNDATION", {}).get("open_prs"))
    if foundation_open:
        for sid in slices:
            if sid.startswith("VS-"):
                blocked.append({"slice": sid, "reason": "FOUNDATION has open execution; do not infer readiness until owning gates are approved."})

    work_queue = {"ready": [], "blocked": [], "in_progress": [], "in_review": []}
    if live["status"] == "known":
        for issue in live["issues"]:
            if issue.get("state") != "open":
                continue
            sid = issue_slice(issue)
            if not sid or sid not in execution:
                continue
            blockers = issue_blockers(issue)
            unresolved = []
            unknown = []
            for blocker in blockers:
                if blocker == int(issue["number"]):
                    findings.append(finding("issue.self_blocked", "error",
                        f"Issue #{issue['number']} blocks itself.", issue=issue["number"]))
                    unresolved.append(blocker)
                    continue
                target = issue_by_number.get(blocker)
                if target is None:
                    unknown.append(blocker)
                    findings.append(finding("issue.unknown_blocker", "warning",
                        f"Issue #{issue['number']} references unknown blocker #{blocker}.",
                        issue=issue["number"], blocker=blocker))
                elif target.get("state") != "closed":
                    unresolved.append(blocker)
            linked_prs = prs_by_issue.get(int(issue["number"]), [])
            if unresolved or unknown:
                state = "blocked"
            elif any(not pr.get("draft", False) for pr in linked_prs):
                state = "in_review"
            elif linked_prs:
                state = "in_progress"
            else:
                state = "ready"
            work_queue[state].append({
                "issue": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "slice": sid,
                "capabilities": issue_capabilities(issue, caps),
                "blocked_by": unresolved,
                "unknown_blockers": unknown,
                "pull_requests": [
                    {"number": pr["number"], "title": pr["title"], "url": pr["html_url"], "draft": pr.get("draft", False)}
                    for pr in linked_prs
                ],
            })
        for state in work_queue:
            work_queue[state].sort(key=lambda item: (slices.index(item["slice"]), item["issue"]))

    trigger_by_cap = {t["capability"]: t for t in triggers["triggers"]}
    watch = []
    for cid, cap in caps.items():
        if cap["status"] == "watch":
            trig = trigger_by_cap.get(cid)
            watch.append({"capability": cid, "activation_condition": trig.get("condition") if trig else "missing trigger"})

    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("error", "warning", "info")}
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": os.environ.get("GITHUB_REPOSITORY", "fusumivietnam/SongChart-Next"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD") or "unknown",
            "commit": git("rev-parse", "HEAD") or "unknown",
        },
        "authority": {
            "policy": "docs/roadmap/ROADMAP_GOVERNANCE.md",
            "scope": "docs/roadmap/VERTICAL_SLICES.md",
            "lifecycle": "governance/CAPABILITY_MAP.json",
            "execution": "live GitHub Issues/PRs",
            "evidence": "exact-SHA CI/release/deployment records",
            "projects": "derived view only",
        },
        "live_github": {"status": live["status"], "reason": live.get("reason"), "truncated": live.get("truncated", False)},
        "slices": [{"id": sid, **execution[sid]} for sid in slices],
        "active_execution": active,
        "blocked_slices": blocked,
        "work_queue": work_queue,
        "watch_capabilities": watch,
        "findings": findings,
        "summary": {"planned_slices": len(slices), "capabilities": len(caps), "technologies": len(technologies["technologies"]), **counts},
    }

def render_text(report):
    s = report["summary"]
    print(f"SongChart roadmap health | {report['source']['branch']} @ {report['source']['commit']}")
    print(f"Live GitHub: {report['live_github']['status']}; slices={s['planned_slices']}; capabilities={s['capabilities']}")
    print(f"Findings: {s['error']} error, {s['warning']} warning, {s['info']} info")
    if report["active_execution"]:
        print("Active execution:")
        for item in report["active_execution"]:
            print(f"  {item['slice']}: {len(item['open_issues'])} open issue(s), {len(item['open_prs'])} open PR(s)")
    else:
        print("Active execution: none known (or live state unavailable)")
    if report["blocked_slices"]:
        print("Conservative blockers:")
        for item in report["blocked_slices"]:
            print(f"  {item['slice']}: {item['reason']}")
    for f in report["findings"]:
        print(f"[{f['severity'].upper()}] {f['code']}: {f['message']}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-github", action="store_true", help="Read Issues/PRs through GitHub REST; read-only.")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "fusumivietnam/SongChart-Next"))
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--output-json", help="Also write the derived report to this path.")
    ap.add_argument("--fail-on-error", action="store_true", help="Exit non-zero only for controller errors, never warnings/blockers.")
    args = ap.parse_args()
    live = fetch_live(args.repo, args.token) if args.live_github else {"status": "unknown", "reason": "offline mode", "issues": [], "pull_requests": []}
    report = derive(live)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        render_text(report)
    if args.fail_on_error and report["summary"]["error"]:
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
