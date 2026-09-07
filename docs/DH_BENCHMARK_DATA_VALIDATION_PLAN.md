# Dartmouth Health Benchmark Data Validation Plan

Purpose: turn the current Dartmouth Health benchmark assessment framework into a data-backed benchmark without overclaiming.

## Non-negotiable rule

Do not score Dartmouth Health unless the row has a source, a finding, a confidence level, and a traceable rationale. The public website must continue to say the benchmark is a framework until evidence collection is complete.

## Current state

The public benchmark page is a framework. It defines the domains and evidence needed to assess maturity. It is not a completed scored evaluation.

Known public evidence already identified:

1. ConnectShareCare public story page: Dartmouth Health-supported patient and care partner engagement asset.
2. Dartmouth Health news release on ConnectShareCare: describes the platform, intended users, and relationship to the Promise Partnership Coproduction Learning Health System.
3. Promise Partnership public pages: describe DH and The Dartmouth Institute coproduction learning health system work.
4. Promise Partnership learning collaboratives page: describes the Care Experience Collaborative and other learning structures.
5. Peer-reviewed Promise Partnership case study: supports the coproduction learning health system framing.
6. AHRQ PSSM Domain 5 resources: external benchmark for patient and family engagement, including PFAC input on safety.

## Evidence collection table

Create or update a structured evidence table with these fields:

| Field | Meaning |
|---|---|
| domain | One of the benchmark framework domains. |
| evidence_item | Specific document, page, meeting artifact, measure, or stakeholder input. |
| evidence_type | Public web source, peer-reviewed article, project document, stakeholder input, metric, or internal artifact. |
| source_title | Human-readable source title. |
| source_url | Public URL when available. Leave blank for non-public documents. |
| date_reviewed | Date the evidence was reviewed. |
| current_finding | What the evidence actually supports. |
| limitation | What the evidence does not prove. |
| confidence | High, moderate, low, or insufficient. |
| gap | What still needs to be verified. |
| recommended_action | Practical next step for DH or the toolkit. |
| public_safe | Yes or no. |
| include_on_site | Yes or no. |

## Domains to validate

1. Engagement infrastructure
2. PFAC authority
3. PSSM 5 alignment
4. Learning health system connection
5. Measurement and feedback
6. Equity and representation
7. Spread and sustainability

## Scoring rule

Use scores only after evidence exists.

Suggested scale:

| Score | Label | Requirement |
|---|---|---|
| 0 | Not assessed | No reliable evidence reviewed. |
| 1 | Emerging | Evidence of activity exists, but no clear governance or measurement link. |
| 2 | Developing | Structure exists and some evidence of use is available, but follow-through is incomplete or undocumented. |
| 3 | Established | Clear structure, owner, cadence, and some closed-loop evidence. |
| 4 | Integrated | Engagement is linked to safety, experience, equity, measurement, and leadership decisions. |
| 5 | Learning system | Evidence shows continuous learning, spread, feedback to participants, and measurable improvement. |

Do not publish a numeric score on the public site until at least two evidence items support the score for that domain or the limitation is clearly stated.

## Source review instructions

For each source:

1. Record the exact claim the source supports.
2. Do not infer governance authority unless the source documents governance authority.
3. Do not infer measurement or outcomes unless the source reports measurement or outcomes.
4. Separate lived experience from peer-reviewed evidence.
5. Separate public evidence from internal or restricted evidence.
6. Use public-safe language only on the website.
7. Keep raw project notes out of the public site.

## Public website update instructions

After evidence collection:

1. Keep the page title as Dartmouth Health Benchmark.
2. Keep the page label as Benchmark assessment framework unless scoring is complete.
3. Add a section titled Evidence-backed preliminary findings only when there are traceable findings.
4. Use plain labels: Publicly supported, Not yet validated, Insufficient evidence, Preliminary finding.
5. Do not use final-sounding language such as proven, certified, complete, definitive, or scored unless the evidence supports it.
6. Do not mention private repositories, internal development, deployment, or administrative tooling.
7. Keep links inside the public reviewer flow.

## Regression expectations

The regression suite should fail if the DH benchmark page:

1. Calls itself a completed scorecard without evidence.
2. Uses Benchmark maturity model as the public label.
3. Uses maturity score before scoring evidence exists.
4. Removes the not-yet-scored disclosure.
5. Removes the evidence-status table.
6. Removes the distinction between publicly supported and not yet validated items.
7. Introduces prompt artifacts, raw markdown, or internal administrative language.

## Done criteria

The benchmark becomes data-backed only when:

1. Every domain has at least one reviewed evidence item.
2. Every public claim has a public source or is clearly marked as preliminary.
3. Every non-public finding is summarized without exposing restricted material.
4. Each domain has a finding, confidence level, gap, and recommended action.
5. The public page passes regression and reads like a health system improvement product, not a project scratchpad.
