# APE PFAC Leadership Toolkit

This repository contains an MPH Applied Practice Experience focused on Patient and Family Advisory Councils, patient and family engagement, and the CMS Patient Safety Structural Measure, Domain 5: Patient and Family Engagement.

## Purpose

The project translates current PFAC evidence, federal guidance, local population context, and patient experience considerations into two practical host-site deliverables:

1. An environmental scan with executive synthesis and annotated bibliography.
2. A PFAC leadership toolkit with reusable assessment, governance, representation, action-tracking, measurement, and Domain 5 traceability tools.

The APE is a non-research applied practice project. It does not claim that PFAC presence alone causes better patient safety, experience, or clinical outcomes.

## APE to ILE scholarly bridge

The public APE remains the applied practice product. A separate planning artifact, `docs/ILE_RESEARCH_BLUEPRINT.md`, defines a proposed scholarly bridge into the Integrative Learning Experience: a structured evidence synthesis examining the organizational, governance, and implementation conditions that help formal patient and family engagement translate into accountable health-system action.

The ILE blueprint does not convert the APE into research, does not treat local APE observations as research findings, and is not a submitted ILE paper. It is a controlled research-planning layer intended for refinement with the ILE faculty mentor.

## Lived-experience anchor

Rosie Bartel's public story is used as a lived-experience design lens for dignity, communication, escalation, infection prevention, and system learning. It is kept separate from peer-reviewed evidence and is not presented as representative evidence or proof of PFAC effectiveness.

## Faculty-facing evidence discipline

The project distinguishes among:

- federal requirements and guidance;
- empirical findings;
- conceptual frameworks;
- implementation recommendations;
- local descriptive analysis;
- proposed leadership actions;
- lived-experience material.

Current evidence supports PFACs as a formal patient and family engagement structure, while rigorous evidence directly linking PFACs to downstream safety, satisfaction, or clinical outcomes remains limited. Claims are therefore calibrated to the strength and design of their sources.

## Applied local analysis

The site includes a reproducible descriptive re-analysis of the Dartmouth Hitchcock Medical Center and Alice Peck Day Memorial Hospital 2025 Upper Valley service-area data. The analysis uses 19 municipalities and a 72,736-person denominator to examine age, disability, poverty, and access-related context relevant to PFAC representation and participation design.

The analysis is presented as a clean interactive evidence table rather than a decorative dashboard. Reviewers can inspect the municipality-level rows, benchmarks, calculation logic, interpretation, and limitations directly.

## APE competency proof

The two deliverables demonstrate the five competencies selected in the APE Agreement:

1. CEPH 4: interpret results of data analysis for public health research, policy, or practice.
2. CEPH 7: assess population needs, assets, and capacities that affect communities' health.
3. CEPH 16: apply leadership and management principles to address a relevant issue.
4. CEPH 21: integrate perspectives from other sectors and professions to promote and advance population health.
5. Dartmouth program-specific competency 4: compare approaches to engaging target populations in decision making, design, governance, and delivery of services, including implications for quality, safety, equity, and value.

## Comparative toolkit scan

The project compares established PFAC and patient/family engagement resources from AHRQ, IPFCC, AMA STEPS Forward, Betsy Lehman Center, health-system examples, and the learning health system literature. The goal is not to claim superiority over those resources. The APE adapts their strengths into a single leadership workflow with Domain 5 traceability, local population context, evidence limitations, action ownership, measurement, and report-back.

## Quality controls

A dedicated faculty review gate runs with the regression suite on each change to `main`. It checks core evidence language, competency traceability, APE scope, claim boundaries, patient-story separation, local-analysis integrity, unfinished-content language, and public-page spillover.

Key controls include:

- no unsupported Dartmouth Health maturity or outcome claims;
- no conflation of patient stories with empirical evidence;
- no public build, model, prompt, or internal tooling language;
- no unfinished public placeholders;
- recomputation of the Upper Valley analysis from the source CSV;
- regression coverage for the interactive analysis, contextual navigation, and retired-route guards.

## Architecture

- Python standard-library web service
- Static HTML/CSS/JavaScript front end
- JSON API routes
- Supabase-backed de-identified demonstration intake and toolkit data
- Render deployment

Legacy technical identifiers retain `pssm5` in package, repository, Supabase, and Render names to avoid breaking deployed infrastructure. Public-facing terminology uses **CMS Patient Safety Structural Measure, Domain 5: Patient and Family Engagement**.

## Local run

```bash
pip install .
pssm5-toolkit-web
```

Open `http://localhost:8765`.

## Public service

The Render service is deployed from the `main` branch and serves the public APE toolkit.

## Data and privacy boundary

The demonstration intake is limited to sanitized, de-identified notes. Do not enter PHI, MRNs, dates of birth, or private patient details. Supabase Row Level Security is enabled on public-schema tables used by the project.

## Key project files

- `docs/ILE_RESEARCH_BLUEPRINT.md`
- `docs/GEISEL_FACULTY_REVIEW_PROTOCOL.md`
- `docs/GEISEL_FACULTY_SITE_REVIEW.md`
- `scripts/faculty_review.py`
- `tests/test_web_contract.py`
- `tests/test_interactive_analysis.py`
- `web/evidence-summary.html`
- `web/evidence-matrix.html`
- `web/applied-analysis.html`
- `web/upper-valley-local-analysis.csv`
- `web/deliverables.html`
- `web/toolkit-tools.html`
