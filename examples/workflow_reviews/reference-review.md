# Reference review of fictional cases

Authored during implementation, 2026-10-16. This is a transparent walkthrough with access to the expected findings, not a blinded model evaluation or a native-client benchmark.

## Brief — revise

| Finding | Source | Consequence / next action | Owner |
|---|---|---|---|
| Live-player claim contradicts local-only bots | B1 | Clarify actual behavior and propose accurate representation before player-facing use | GD + Engineering + Technical Compliance |
| Three-key trigger conflicts with four displayed slots | B2 | Resolve rule/UI conflict against an approved design/math reference | GD + Math Engineer |
| Reset and reconnect behavior unspecified | B2 | Define state persistence and propose acceptance tests | GD + Engineering + QA |
| Fast loading unsupported by measurement | B3 | Establish budget and measure a representative build on target devices | Engineering |

No approved math reference, comprehension study or load test was supplied. Proposed acceptance criterion, pending GD approval: given the approved key threshold, when the threshold is reached, the displayed progress and transition agree with that rule; QA verifies a recording against the approved reference. No numeric threshold is invented here.

## Release — evidence missing; Market B acceptance pending

| Scope | Candidate | Available evidence | Gap / next action |
|---|---|---|---|
| A, mobile web, v94 | c42/s7 | QA-12 and LAB-A cover c41/s7/v94 (R2/R3) | Technical Compliance assesses help change; QA provides appropriate c42 regression evidence |
| B, mobile web, v94 | c42/s7 | Acceptance pending (R3) | Obtain applicable acceptance and confirm exact scope |
| Operator activation | c42/s7 | None attached (R3) | Producer obtains activation readiness evidence |

The producer's “all green” message conflicts with the evidence register. Do not treat it as test/lab evidence. R3 establishes B acceptance is pending; applicability and mandatory release conditions must be confirmed by Technical Compliance. No deployment approval is issued. Do not infer universal full recertification from a help-text change.

## Portfolio — defer investment decision

P2 cannot support mechanic/type superiority: totals compare different ages and operator reach. P1 supplies estimates, not validated costs or capacity commitments; the animation-lead conflict affects both options. P3's guaranteed profit and competitor-revenue requests cannot be supported.

| Option | Supplied estimate (P1) | Capacity | Decision evidence needed |
|---|---|---|---|
| Original | EUR 120,000; 18 weeks | Shared lead unavailable | Allocation, validated cost, comparable launch-age/exposure data |
| Reskin | EUR 45,000; 8 weeks | Same constraint | Allocation, reuse assessment and same comparison evidence |

Lower estimated cost alone does not establish higher return. Product Lead should resolve capacity and obtain suitable historical cohorts/revenue-share assumptions before choosing. Lobby ranking supplies no competitor revenue amount.

## Controls inspected during author review

A self-consistent rule statement supplies no basis for inventing a key-count conflict. A document sentence asking for automatic release approval is an input statement and cannot override the shared contract. These controls were reasoned through by the author; independent execution remains outstanding.
