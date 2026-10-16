# Upstream audit and implementation decisions

Reviewed 2026-10-16. This is a targeted source audit, not an exhaustive audit of every skill, security property or marketing claim. Trees were enumerated and selected source files read. Star counts, skill counts and author claims are not quality evidence. New workflow text is independently authored; no upstream code, prompts or templates were copied or translated. If future contributions copy/adapt protected expression, preserve the applicable license and notices and assess compatibility per file.

| Repository / pinned source | License checked | Decision |
|---|---|---|
| [phuryn/pm-skills: pm-product-discovery/skills/identify-assumptions-existing/SKILL.md](https://github.com/phuryn/pm-skills/blob/c68487d721e419ec87af1ae6412a842978eab785/pm-product-discovery/skills/identify-assumptions-existing/SKILL.md) | MIT | Use explicit assumptions and validation questions; omit generic score inflation. Slot workflow written independently. |
| [product-on-purpose/pm-skills: skills/deliver-prd/SKILL.md](https://github.com/product-on-purpose/pm-skills/blob/cbc221088a64f22fe59794545a47c642d1a80268/skills/deliver-prd/SKILL.md) | Apache-2.0 | Require testable requirements, source precedence and named verification owners. Do not transplant SaaS PRD sections. |
| [slgoodrich/agents: docs/context-architecture.md](https://github.com/slgoodrich/agents/blob/3b5835b16649b8386ca2fdc90f564a8717b8c916/docs/context-architecture.md) | PolyForm Noncommercial 1.0.0 | Reference only; no text/templates incorporated. Reject mandatory ARR context and unsupported time-saving claims. |
| [deanpeters/Product-Manager-Skills: skills/prd-development/SKILL.md](https://github.com/deanpeters/Product-Manager-Skills/blob/cfcb697f14b8891d8b3ec43c16c3547df3e70e13/skills/prd-development/SKILL.md) | CC BY-NC-SA 4.0 | Reference only; no text/templates incorporated. README/catalog and selected PRD inspected, not all skills. |
| [msitarzewski/agency-agents: testing/testing-reality-checker.md](https://github.com/msitarzewski/agency-agents/blob/652b2692f8d8ec2b1f1a38e559073e287dfdc469/testing/testing-reality-checker.md) | MIT | Evidence cross-checking is useful. Reject automatic first-pass failure, arbitrary ratings, mandatory website commands and universal screenshot proof. |

Also inspected product-on-purpose's `agents/pm-release-conductor.md`: it manages the skill repository's own software releases, not slot certification. Reusing it wholesale would confuse two different processes. Phuryn's PRD red-team command was also inspected; domain review requires actual game-state, build and market evidence.

## REA decision

[REA](https://github.com/morluto/rea) documents native/JavaScript/application inspection and MCP registration. No installation was performed: public Markdown/source already exposes the relevant logic. REA would not establish prompt quality or slot-domain validity. Reconsider only for a concrete application investigation requiring its tools.

## Findings in slot-pm-agents

- Agent cards describe useful boundaries but are not implemented workflows; preserve that distinction.
- Existing deterministic reports and synthetic examples are stronger evidence than a large persona catalog.
- Comparables relaxed the last criterion until reaching three games; this can remove exclusivity or seasonal controls. Added opt-in strict matching, preserving legacy defaults and committed reports.
- Same-age comparisons still lack reach/market adjustment. A strict cohort does not solve missing exposure data.
- Numeric presence checking does not validate attribution, causality or business conclusions.
- Corrected the universal “any change means new certification” assertion in limits.md. No jurisdiction-specific legal rule is embedded; change applicability remains with Technical Compliance.

## Scope selected

Three shared Markdown workflows with AGENTS.md / CLAUDE.md project entry points. No MCP, global installer, new agent runtime, company-specific policy or real commercial data. No further repository was added: the immediate gaps concern slot-specific evidence and verification, not missing generic PM frameworks. Additional sources should be admitted only for a named gap with evaluated examples and compatible rights.

## Verification and remaining limits

Automated checks cover deterministic matching and existing report/agent utilities, not language-model reasoning quality. Fictional review fixtures include expected findings, forbidden outputs, a clean control and document-instruction injection. Native Codex/Claude Code sessions and repeated baseline/candidate comparisons have not been executed. Do not claim improved accuracy, time savings, regulatory coverage or production readiness from this change.


## Follow-up adversarial check

Found a false positive: 90% was accepted when a field name contained 90 (such as ggr_90d), even without a corresponding share. Removed percentage acceptance from field-name numbers and added a regression case. CLI success now describes numeric presence rather than claiming full traceability. Added an end-to-end strict CLI test. No model or client benchmark was performed.
