# Review slot release evidence

Read `docs/assistant-contract.md`. Produce an evidence assessment for a defined release, never a deployment authorization.

Inputs: intended release scope/date, target markets/operators/platforms, exact client/server/build identifiers, RTP/configuration variants, QA results and open defects, certification records, change list, integration dependencies, rollback/disable plan and accountable owners.

1. Build a matrix per market/platform/configuration. Link the exact artifact/version to QA evidence, certification/change-assessment evidence, operator readiness and human sign-off. A filename containing “approved” is not approval evidence.
2. Compare tested, submitted, approved and intended-to-deploy identities. Flag mismatches, pending dependencies and post-test changes. A server approval does not establish client approval. Do not transfer one market's acceptance to another.
3. Check open defects, regression scope, localization/help, interrupted-round recovery, configuration and applicable responsible-gambling evidence. Mark absent evidence unknown; use supplied acceptance criteria, not invented universal release gates.
4. Ask Technical Compliance to assess changes to certified scope. Do not claim every change automatically requires full recertification; treatment depends on the change, jurisdiction and applicable process. Do not alter frozen builds.
5. Record dependency owners, required evidence, next actions and the decision deadline. Distinguish product review, QA completion, lab acceptance, production deployment and operator activation.
6. Present a scoped recommendation. A clear market may be considered separately only by the authorized people with a verified configuration separation; never recommend bypassing pending mandatory acceptance.

Use the shared output contract plus the market/build evidence matrix. Missing QA or certification attachments cannot be marked passed from a status summary alone.
