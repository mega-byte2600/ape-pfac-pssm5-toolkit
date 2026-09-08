# Geisel Faculty Site Review

Review date: 2026-09-07
Final hardening completed: 2026-09-08

Reviewer role: faculty-level review of the MPH Applied Practice Experience as an applied public health and health-system improvement product.

## Faculty decision

**Status: faculty-ready for preceptor review and public demonstration.**

The project now presents a coherent applied practice product rather than a development environment. The public site clearly separates evidence, local descriptive analysis, implementation guidance, lived experience, proposed leadership action, and items requiring host validation.

The APE remains two practical host-site deliverables:

1. Environmental scan with executive synthesis and annotated bibliography.
2. PFAC leadership toolkit/playbook with reusable assessment, governance, representation, action-tracking, measurement, and CMS Patient Safety Structural Measure Domain 5 traceability tools.

The site does not represent the APE as human-subjects research and does not combine it with a separate Integrated Learning Experience.

## Faculty concerns resolved

### Evidence calibration

Resolved. The Evidence-Based PFAC Summary and Evidence Matrix explicitly state that rigorous evidence directly linking PFACs to patient safety, patient satisfaction, or clinical outcomes remains limited. Cross-sectional findings, reviews, conceptual frameworks, federal guidance, and implementation recommendations are labeled according to evidence type and limitation.

### Current PFAC evidence

Resolved. The evidence layer includes current 2025 and 2026 PFAC literature, including work on PFAC use, predictors of council effectiveness, patient safety applications, and diverse recruitment and engagement. The bibliography is synchronized with the evidence matrix and includes a citation-validation note.

### CMS terminology

Resolved. Public-facing language uses **CMS Patient Safety Structural Measure, Domain 5: Patient and Family Engagement**. Legacy `pssm5` terminology remains only in technical identifiers where changing it would break deployed infrastructure.

### CEPH 4: interpretation of data analysis

Resolved. The Applied Analysis page contains a reproducible local descriptive re-analysis of the 2025 Upper Valley service area using the same 19-municipality CSV served by the site. Reviewers can inspect the denominator, benchmark, municipality-level values, result, interpretation, and limitations through a clean interactive table.

Validated headline findings:

- 48.4% of service-area residents live in municipalities where the published poverty percentage is above the 8% service-area average.
- 60.5% live in municipalities where the published disability percentage is above the 12% service-area average.
- 47.9% live in municipalities where the published age 65+ percentage is above the 22% service-area average.

These are planning signals, not clinical risk scores or causal findings.

### CEPH 7: population needs, assets, and capacities

Resolved. The project defines the Upper Valley service-area population and translates local age, disability, poverty, access, navigation, rurality, isolation, transportation, caregiver, and technology considerations into PFAC recruitment and participation requirements.

### CEPH 16: leadership and management

Resolved. The leadership toolkit includes executive ownership, governance, disposition, accountable owner, due date, escalation, action closure, measurement, report-back, and reassessment.

### CEPH 21: integration of perspectives

Resolved with claim boundary preserved. The project integrates perspectives from empirical research, federal guidance, patient/family engagement organizations, health-system examples, local community-health evidence, and lived-experience material. It does not claim direct patient co-design or local stakeholder participation where those activities have not occurred.

### Dartmouth program-specific competency 4

Resolved. The project contains comparative toolkit and engagement analysis using common dimensions related to decision making, design, governance, delivery, safety, quality, equity, value, representation, and accountability.

### Dartmouth Health benchmark

Resolved. The benchmark is presented as a structured assessment framework, not a completed maturity score or completed organizational evaluation. Evidence states remain separated as publicly supported, preliminary, not yet validated, or insufficient evidence.

### HAI/MRSA use case

Resolved. The former dashboard placeholder was replaced with a finished table-first evidence signal and synthesis. The page now connects infection prevention, discharge readiness, warning signs, escalation, patient concerns, local-data review, and leadership follow-through without using decorative charts or unfinished loading states.

### Patient story and evidence separation

Resolved. Rosie Bartel is presented as a public lived-experience anchor, not research evidence, not representative evidence, and not an endorsement of the project. Her story is used to test dignity, communication, escalation, and safety questions.

### About and collaboration pages

Resolved. The About page is concise and focused on project lead/contact information and reviewer links. The Collaboration page is operational: what to submit, what not to submit, how review works, and how accepted contributions may enter the evidence or toolkit workflow.

### Reviewer flow

Resolved. The former Reviewer Readiness page is now a simple Reviewer Guide and is explicitly a navigation aid rather than a substantive deliverable.

## Quality and regression controls

A dedicated faculty review gate runs with the web regression suite on each change to `main`.

The faculty gate checks:

- evidence limitations;
- current evidence references;
- APE scope;
- competency traceability;
- local-analysis requirements;
- patient-story boundaries;
- Dartmouth Health claim boundaries;
- public-page generation/tooling spillover.

The regression suite additionally checks:

- every public page loads directly rather than falling back to the homepage;
- interactive analysis controls and JavaScript are served;
- the 19-municipality analysis recomputes to the published results;
- no charting layer is used for the local analysis;
- no unfinished HAI placeholder language remains;
- no unsupported maturity or outcome claims appear;
- no raw Markdown artifacts appear on public pages;
- public pages do not expose internal model, prompt, repository, deployment, or build-language artifacts.

## Technical review

Supabase public-schema tables have Row Level Security enabled. The demonstration intake is restricted to de-identified content and is not intended for PHI. The public intake Edge Function remains a demonstration endpoint and should receive additional abuse controls such as rate limiting before any broader production intake use.

## Final faculty assessment

The project's strongest feature is now the full traceable chain:

**patient and community need → evidence → limitation → local context → leadership action → ownership → measurement → report-back.**

That chain is visible to a faculty reviewer and usable by a health-system leader. The APE is ready to move from build mode into preceptor review, dissemination, and subsequent ILE work while preserving a clear boundary between applied practice and future research.
