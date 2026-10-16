# Review a slot brief and signposting

Read `docs/assistant-contract.md`. Review supplied evidence; do not silently rewrite approved design.

Inputs: brief/version, player flow or state diagram, feature rules, approved math references if available, platforms/markets, asset/performance constraints, business objective and available research.

1. Restate the proposition, target audience, scope and success hypothesis. Distinguish operator adoption from player comprehension. A commercial aspiration is not evidence of demand.
2. Trace base game → trigger → feature → retrigger/exit → settlement. For each state, ask what the player sees, why it happened, what action is available, how progress/reset works and what the displayed reward means. Cover interrupted sessions, reconnect, localization, mobile readability and rules/help consistency. Do not invent a missing feature rule.
3. Flag mismatches among brief, UI, help, math reference and platform behavior. Highlight real versus simulated social/multiplayer claims; ask Engineering to establish server/shared-state feasibility and request Compliance review of player-facing representation.
4. Examine delivery assumptions: asset size, loading budget, streaming/client constraints, dependencies and reuse. Require measured performance evidence and agreed target devices before treating an optimization as proven.
5. For each major assumption propose the smallest useful validation: comprehension test, technical spike, deterministic rule test or owner review. Do not turn arbitrary RICE scores into evidence.
6. Propose acceptance criteria only for supplied/explicitly proposed behavior. Tag proposals as unapproved. Include Given/When/Then plus verifier role, evidence artifact and linked source. Route unresolved rules to GD/Math rather than completing them yourself.

Use the shared output contract plus a state/signposting gap table and a short scope recommendation. Keep the review proportional to the brief.
