# The 7 layers, adapted to a slot studio

This framework comes from general product management (strategy, roadmap, business case, define, build, measure, run). Below, each layer is rewritten for a slot **studio** (a game provider), not an operator (a casino).

The unit of product is **a game inside a portfolio**, not a feature.

## Overview

| # | Layer | Agents | Person who decides | Agent value | Risk |
|---|---|---|---|---|---|
| 1 | Strategy | Market scan, Operator signal | Head of Games | High | Low |
| 2 | Roadmap | Release planner | Head of Product | Medium | Low |
| 3 | Business case | Cost estimator, Comparables | Product Lead | High for cost, low for revenue | Medium |
| 4 | Define | Brief writer, Math spec drafter | Game Designer, Math Engineer | Medium | High for math |
| 5 | Build | QA case writer, Cert pack assistant | Producer | Low to medium | High |
| 6 | Measure | Performance review | Product Lead | High | Low |
| 7 | Run | Jurisdiction tracker | Producer, Live Ops | Medium | Medium |

## 1. Strategy

**Goal:** turn market signals into game options.

- Track competitor releases: theme, mechanic, grid, volatility, max win, release date.
- Track operator feedback and requests.
- Track regulation changes per market (stake limits, feature bans, speed of play).

**Data:** public release lists, demo pages, press releases, operator emails.
**Human decision:** which bets the studio makes this year.
**Limit:** you never see competitor revenue. Popularity signals (lobby position, streamer use) are weak proxies.

## 2. Roadmap

**Goal:** a release calendar that fits capacity.

- Draft scenarios: in-house vs vendor, original vs reskin.
- Check certification and marketing lead times (roadmap slot, promo materials, demo links).
- Keep portfolio balance: volatility mix, themes, mechanics.

**Data:** milestone templates, team and vendor capacity.
**Human decision:** the calendar.
**Limit:** priority in a studio is commercial and political. A good spreadsheet does 80% of this layer.

## 3. Business case

**Goal:** cost every option and show the expected return as a range.

- Cost per discipline (art, animation, front end, math, audio, QA, certification, translation) from past projects.
- Weeks per milestone from past projects, with historical slip.
- Revenue range from comparable games (same family, mechanic, volatility), normalised by days live.

**Data:** `costs`, `milestones`, `daily_performance`.
**Human decision:** which option goes ahead.
**Limit:** the revenue of a game that does not exist is not predictable. Show a range and the comparables, never one number.

## 4. Define

**Goal:** a clear spec the team and vendors can build from.

- Draft the game design document from the approved case.
- Write art, animation and audio briefs for vendors.
- Draft stories and acceptance criteria, including compliance criteria per market.
- Draft a math spec: target RTP, volatility, hit rate, max win, feature frequency.

**Human decision:** Game Designer owns the design. Math Engineer owns the math.
**Limit:** the math draft must be simulated and signed off by a person. Never ship math an agent produced.

## 5. Build

**Goal:** deliver a certified build.

- Write QA test cases from acceptance criteria.
- Prepare the certification pack (documents, math reports, change log).
- Summarise vendor weekly reports and flag risk.

**Human decision:** Producer owns delivery and sign-off.
**Limit:** certified builds are frozen. Agents do not write production game code and do not deploy.

## 6. Measure

**Goal:** know what each release actually did.

- GGR and bets at 30, 90 and 180 days after launch.
- Actual RTP vs theoretical RTP.
- Actual cost vs budget, actual weeks vs plan.
- Compare against the business case.

**Data:** `daily_performance`, `costs`, `milestones`.
**Human decision:** Product Lead reviews. Results feed layer 1 and layer 3.
**Limit:** a studio often sees less player data than an operator. Measure what you have; do not invent retention metrics you cannot see.

See the working example in [`examples/portfolio_review`](../examples/portfolio_review/).

## 7. Run

**Goal:** keep live games healthy and compliant.

- Track RTP variants per jurisdiction.
- Flag games affected by new rules.
- Suggest games to retire or to reskin.

**Human decision:** Producer and Live Ops.
**Limit:** incident handling and platform upgrades are engineering work, outside product.

## Cross-cutting rules

- **Regulation** applies at every layer, not only at certification.
- **Responsible gambling** is a criterion in every decision.
- **Every agent output names its sources** and its confidence.
