#!/usr/bin/env python3
"""Project #2 projection sync.

Reads SongChart roadmap authority + live Issues/PRs, then mirrors deterministic
execution metadata into a GitHub Projects v2 board. The Project is a derived
view only; this script never mutates repository authority, Issues, or PRs.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    from scripts import roadmap_health as health
except ModuleNotFoundError:  # Direct execution: python3 scripts/project_sync.py
    import roadmap_health as health

ROOT = Path(__file__).resolve().parents[1]
CAPABILITY_MAP = ROOT / "governance" / "CAPABILITY_MAP.json"
WORK_MANAGEMENT = ROOT / "governance" / "GITHUB_WORK_MANAGEMENT.json"

FIELD_SPECS = {
    "Slice": {"type": "SINGLE_SELECT"},
    "Capability": {"type": "SINGLE_SELECT"},
    "Execution": {
        "type": "SINGLE_SELECT",
        "options": ["Proposed", "Ready", "In progress", "Blocked", "In review", "Done"],
    },
    "Gate": {"type": "SINGLE_SELECT", "options": ["G0", "G1", "G2", "G3", "G4", "G5"]},
    "Decision": {
        "type": "SINGLE_SELECT",
        "options": ["None", "Owner decision required", "Approved", "Rejected"],
    },
    "Evidence": {"type": "TEXT"},
}
def load_work_management():
    data = json.loads(WORK_MANAGEMENT.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("project") != "SongChart-Next":
        raise RuntimeError("invalid GitHub work-management contract")
    return data


def required_views():
    return list(load_work_management()["github_project"]["required_views"])

META_GATE_RE = re.compile(r"\*\*Project Gate:\*\*\s*(G[0-5]|none)", re.I)
META_DECISION_RE = re.compile(
    r"\*\*Project Decision:\*\*\s*(None|Owner decision required|Approved|Rejected)",
    re.I,
)
VERIFY_RE = re.compile(r"\*\*Verification evidence:\*\*\s*([^\n]+)", re.I)


def graphql(token, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "songchart-project-projection",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub GraphQL request failed: {type(exc).__name__}") from exc
    if payload.get("errors"):
        messages = "; ".join(error.get("message", "unknown GraphQL error") for error in payload["errors"])
        raise RuntimeError(f"GitHub GraphQL error: {messages}")
    return payload["data"]


def load_capabilities():
    data = json.loads(CAPABILITY_MAP.read_text(encoding="utf-8"))
    return [item["id"] for item in data["capabilities"]]


def desired_schema():
    slices = health.parse_slices()
    slice_options = []
    for sid in slices:
        name = "Later" if sid == "LATER" else (sid[:-1] + sid[-1].lower() if re.fullmatch(r"VS-\d+[A-Z]", sid) else sid)
        if name not in slice_options:
            slice_options.append(name)
    if "Cross-cutting" not in slice_options:
        slice_options.append("Cross-cutting")
    FIELD_SPECS["Slice"]["options"] = slice_options
    FIELD_SPECS["Capability"]["options"] = load_capabilities()
    return FIELD_SPECS


def projection_metadata(issue):
    body = issue.get("body") or ""
    gate_match = META_GATE_RE.search(body)
    decision_match = META_DECISION_RE.search(body)
    verify_match = VERIFY_RE.search(body)
    gate = gate_match.group(1).upper() if gate_match and gate_match.group(1).lower() != "none" else None
    decision = decision_match.group(1) if decision_match else None
    verification = verify_match.group(1).strip() if verify_match else None
    if verification and verification.lower() in {"pending", "none", "n/a", "-"}:
        verification = None
    return {"gate": gate, "decision": decision, "verification": verification}


def primary_capability(issue, known):
    body = issue.get("body") or ""
    match = health.BODY_CAP_RE.search(body)
    if not match:
        return None
    for candidate in re.findall(r"[a-z0-9][a-z0-9-]+", match.group(1).lower()):
        if candidate in known:
            return candidate
    return None


def issue_execution(report):
    result = {}
    for state in ("ready", "in_progress", "in_review", "blocked"):
        label = {
            "ready": "Ready",
            "in_progress": "In progress",
            "in_review": "In review",
            "blocked": "Blocked",
        }[state]
        for item in report["work_queue"][state]:
            result[int(item["issue"])] = label
    for slice_state in report["slices"]:
        for issue in slice_state["closed_issues"]:
            result[int(issue["number"])] = "Done"
    return result


def linked_pr_evidence(live):
    by_issue = {}
    for pr in live.get("pull_requests", []):
        for issue_number in health.pr_issue_numbers(pr):
            state = "merged" if pr.get("merged_at") else pr.get("state", "unknown")
            by_issue.setdefault(issue_number, []).append(
                f"PR #{pr['number']} ({state}) {pr.get('html_url', '')}".strip()
            )
    return by_issue


def desired_items(live, report):
    known = set(load_capabilities())
    execution = issue_execution(report)
    evidence = linked_pr_evidence(live)
    desired = []
    for issue in live.get("issues", []):
        sid = health.issue_slice(issue)
        if not sid or int(issue["number"]) not in execution:
            continue
        metadata = projection_metadata(issue)
        capability = primary_capability(issue, known)
        if not capability:
            continue
        slice_name = "Later" if sid == "LATER" else (sid[:-1] + sid[-1].lower() if re.fullmatch(r"VS-\d+[A-Z]", sid) else sid)
        evidence_parts = evidence.get(int(issue["number"]), [])[:4]
        if metadata["verification"]:
            evidence_parts.append(metadata["verification"])
        desired.append(
            {
                "number": int(issue["number"]),
                "content_id": issue.get("node_id"),
                "url": issue.get("html_url"),
                "fields": {
                    "Slice": slice_name,
                    "Capability": capability,
                    "Execution": execution[int(issue["number"])],
                    "Gate": metadata["gate"],
                    "Decision": metadata["decision"],
                    "Evidence": " | ".join(evidence_parts) if evidence_parts else None,
                },
            }
        )
    return desired


def project_metadata(token, owner, number):
    query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          title
          fields(first: 100) {
            nodes {
              __typename
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField {
                id name dataType
                options { id name color description }
              }
            }
          }
          views(first: 50) { nodes { id name layout } }
        }
      }
    }
    """
    data = graphql(token, query, {"login": owner, "number": number})
    user = data.get("user")
    project = user.get("projectV2") if user else None
    if not project:
        raise RuntimeError(f"GitHub Project {owner}#{number} not found or token cannot access it")
    return project


def list_project_items(token, project_id):
    query = """
    query($project: ID!, $cursor: String) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              content {
                __typename
                ... on Issue { id number url repository { nameWithOwner } }
              }
              fieldValues(first: 50) {
                nodes {
                  __typename
                  ... on ProjectV2ItemFieldTextValue { text field { ... on ProjectV2Field { name } } }
                  ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2SingleSelectField { name } } }
                }
              }
            }
          }
        }
      }
    }
    """
    cursor = None
    items = []
    while True:
        data = graphql(token, query, {"project": project_id, "cursor": cursor})
        conn = data["node"]["items"]
        items.extend(conn["nodes"])
        if not conn["pageInfo"]["hasNextPage"]:
            return items
        cursor = conn["pageInfo"]["endCursor"]


def create_field(token, project_id, name, spec):
    query = """
    mutation($input: CreateProjectV2FieldInput!) {
      createProjectV2Field(input: $input) {
        projectV2Field {
          __typename
          ... on ProjectV2Field { id name dataType }
          ... on ProjectV2SingleSelectField { id name dataType options { id name color description } }
        }
      }
    }
    """
    payload = {"projectId": project_id, "name": name, "dataType": spec["type"]}
    if spec["type"] == "SINGLE_SELECT":
        payload["singleSelectOptions"] = [
            {"name": option, "color": "GRAY", "description": "SongChart derived projection option"}
            for option in spec["options"]
        ]
    return graphql(token, query, {"input": payload})["createProjectV2Field"]["projectV2Field"]


def ensure_select_options(token, field, expected):
    existing = field.get("options") or []
    existing_names = {option["name"].lower() for option in existing}
    missing = [name for name in expected if name.lower() not in existing_names]
    if not missing:
        return field, []
    options = [
        {
            "id": option["id"],
            "name": option["name"],
            "color": option["color"],
            "description": option.get("description") or "",
        }
        for option in existing
    ]
    options.extend(
        {"name": name, "color": "GRAY", "description": "SongChart derived projection option"}
        for name in missing
    )
    query = """
    mutation($input: UpdateProjectV2FieldInput!) {
      updateProjectV2Field(input: $input) {
        projectV2Field {
          ... on ProjectV2SingleSelectField {
            id name dataType options { id name color description }
          }
        }
      }
    }
    """
    data = graphql(token, query, {"input": {"fieldId": field["id"], "singleSelectOptions": options}})
    return data["updateProjectV2Field"]["projectV2Field"], missing


def ensure_schema(token, project):
    specs = desired_schema()
    fields = {node.get("name"): node for node in project["fields"]["nodes"] if node.get("name")}
    changes = []
    for name, spec in specs.items():
        field = fields.get(name)
        if not field:
            field = create_field(token, project["id"], name, spec)
            fields[name] = field
            changes.append(f"created field {name}")
        if field.get("dataType") != spec["type"]:
            raise RuntimeError(f"Project field {name} must be {spec['type']}, got {field.get('dataType')}")
        if spec["type"] == "SINGLE_SELECT":
            field, missing = ensure_select_options(token, field, spec["options"])
            fields[name] = field
            if missing:
                changes.append(f"added {name} options: {', '.join(missing)}")
    return fields, changes


def item_values(item):
    values = {}
    for node in item.get("fieldValues", {}).get("nodes", []):
        field = node.get("field") or {}
        name = field.get("name")
        if not name:
            continue
        if "text" in node:
            values[name] = node.get("text")
        elif "name" in node:
            values[name] = node.get("name")
    return values


def add_item(token, project_id, content_id):
    query = """
    mutation($project: ID!, $content: ID!) {
      addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
        item { id }
      }
    }
    """
    return graphql(token, query, {"project": project_id, "content": content_id})["addProjectV2ItemById"]["item"]["id"]


def update_field(token, project_id, item_id, field, value):
    if value is None:
        query = """
        mutation($project: ID!, $item: ID!, $field: ID!) {
          clearProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, fieldId: $field}) {
            projectV2Item { id }
          }
        }
        """
        graphql(token, query, {"project": project_id, "item": item_id, "field": field["id"]})
        return
    if field["dataType"] == "TEXT":
        value_input = {"text": value}
    else:
        option = next((o for o in field["options"] if o["name"].lower() == value.lower()), None)
        if not option:
            raise RuntimeError(f"Missing option {value!r} in Project field {field['name']}")
        value_input = {"singleSelectOptionId": option["id"]}
    query = """
    mutation($project: ID!, $item: ID!, $field: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $project, itemId: $item, fieldId: $field, value: $value
      }) { projectV2Item { id } }
    }
    """
    graphql(token, query, {"project": project_id, "item": item_id, "field": field["id"], "value": value_input})


def fetch_issue_node_ids(read_token, repo, desired):
    missing = [item for item in desired if not item.get("content_id")]
    if not missing:
        return
    owner, name = repo.split("/", 1)
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) { issue(number: $number) { id } }
    }
    """
    for item in missing:
        data = graphql(read_token, query, {"owner": owner, "name": name, "number": item["number"]})
        issue = data.get("repository", {}).get("issue")
        if issue:
            item["content_id"] = issue["id"]


def reconcile(project_token, read_token, repo, owner, number, dry_run=False):
    live = health.fetch_live(repo, read_token)
    if live["status"] != "known":
        raise RuntimeError(live.get("reason", "live GitHub state unavailable"))
    report = health.derive(live)
    desired = desired_items(live, report)
    fetch_issue_node_ids(read_token, repo, desired)

    project = project_metadata(project_token, owner, number)
    if dry_run:
        specs = desired_schema()
        fields = {node.get("name"): node for node in project["fields"]["nodes"] if node.get("name")}
        schema_gaps = []
        for name, spec in specs.items():
            if name not in fields:
                schema_gaps.append(f"missing field {name}")
            elif fields[name].get("dataType") != spec["type"]:
                schema_gaps.append(f"{name} has wrong type")
            elif spec["type"] == "SINGLE_SELECT":
                have = {o["name"].lower() for o in fields[name].get("options", [])}
                for option in spec["options"]:
                    if option.lower() not in have:
                        schema_gaps.append(f"{name} missing option {option}")
        return {
            "project": {"id": project["id"], "title": project["title"], "owner": owner, "number": number},
            "dry_run": True,
            "schema_gaps": schema_gaps,
            "desired_items": len(desired),
            "required_views_missing": sorted(set(required_views()) - {v["name"] for v in project["views"]["nodes"]}),
            "changes": [],
        }

    fields, changes = ensure_schema(project_token, project)
    current_items = list_project_items(project_token, project["id"])
    by_number = {}
    for item in current_items:
        content = item.get("content") or {}
        if content.get("__typename") == "Issue" and content.get("repository", {}).get("nameWithOwner") == repo:
            by_number[int(content["number"])] = item

    mutations = 0
    for wanted in desired:
        if not wanted.get("content_id"):
            changes.append(f"skip issue #{wanted['number']}: content node id unavailable")
            continue
        current = by_number.get(wanted["number"])
        if not current:
            if dry_run:
                changes.append(f"would add issue #{wanted['number']}")
                continue
            item_id = add_item(project_token, project["id"], wanted["content_id"])
            current_values = {}
            changes.append(f"added issue #{wanted['number']}")
            mutations += 1
        else:
            item_id = current["id"]
            current_values = item_values(current)
        for field_name, value in wanted["fields"].items():
            previous = current_values.get(field_name)
            if (previous or None) == (value or None):
                continue
            update_field(project_token, project["id"], item_id, fields[field_name], value)
            changes.append(f"issue #{wanted['number']}: {field_name} {previous!r} -> {value!r}")
            mutations += 1

    return {
        "project": {"id": project["id"], "title": project["title"], "owner": owner, "number": number},
        "dry_run": False,
        "desired_items": len(desired),
        "mutations": mutations,
        "changes": changes,
        "required_views_missing": sorted(set(required_views()) - {v["name"] for v in project["views"]["nodes"]}),
        "authority": "derived projection only; repository + live Issues/PRs remain authoritative",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "fusumivietnam/SongChart-Next"))
    parser.add_argument("--owner", default=os.environ.get("PROJECT_OWNER", "fusumivietnam"))
    parser.add_argument("--number", type=int, default=int(os.environ.get("PROJECT_NUMBER", "2")))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    read_token = os.environ.get("GITHUB_TOKEN")
    project_token = os.environ.get("PROJECT_SYNC_TOKEN")
    if not read_token:
        print("GITHUB_TOKEN is required to read live Issues/PRs.", file=sys.stderr)
        return 2
    if not project_token:
        print("PROJECT_SYNC_TOKEN is not configured; Project projection sync skipped.", file=sys.stderr)
        return 3

    try:
        result = reconcile(project_token, read_token, args.repo, args.owner, args.number, args.dry_run)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
