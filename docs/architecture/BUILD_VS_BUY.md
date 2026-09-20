# Build vs reuse

SongChart builds canonical music semantics, provenance, matching/merge policy, provider policy registry, UX semantics and thin integration adapters. Commodity services (workflow, search implementation, deploy, telemetry, asset transforms, docs UI) are evaluated against an observed need before installation.

Order: framework-native -> already approved package -> maintained permissively licensed OSS with a clear boundary -> minimum SongChart-owned implementation. The 80% fit heuristic is advisory, not a waiver of license, security, functionality or migration requirements.

Each new dependency must reference a capability ID and an approved activation trigger, identify overlap with existing capability owners, provide verified compatibility/license evidence and define an exit/retirement plan. No enterprise-only feature becomes an assumed community dependency.
