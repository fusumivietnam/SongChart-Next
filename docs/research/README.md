# Research provenance and disposition

Research is reference material, not a second roadmap or a source of implementation truth. Register only retrievable research in `governance/RESEARCH_REGISTRY.json` using a stable RES-0001 identifier and source path/URL. Never invent an entry for past chat or an inaccessible ZIP. Store project-authored research here when needed; external sources must retain publisher, retrieval date, scope and edition in their research note. Avoid copying old SongChart project authority.

States: registered (not reviewed), evaluated (assessment exists), accepted (evidence useful for a scoped decision), rejected, deferred, superseded. Accepted research **does not approve a capability, a package, a roadmap change, or a deployment**. A decision belongs in its owning ADR/issue and technology adoption in the Technology Registry.

Research note minimum: claim and date, source references, version/edition, applicable capability IDs, relevant alternatives, license/provider rights, security/privacy, limitations and decision link when one exists. A document becomes implemented evidence only when a separate source-linked PR and tests exist. Deprecated research uses `superseded_by` pointing to an existing registered research ID.

Before adding research: check duplicates by topic/source and whether it is already recorded; use unique ID without renumbering existing entries. The registry starts empty on purpose because no independent research corpus has been verified in this repository.
