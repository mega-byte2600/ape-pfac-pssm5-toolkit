# Geisel Faculty Review Protocol

Purpose: provide a standing faculty-level quality gate for the APE website and two host-site deliverables. This protocol is intentionally stricter than ordinary copy review. It tests whether a reviewer can trace the project from the signed APE Agreement to methods, evidence, claims, competencies, and a usable host-site product.

## 1. Scope fidelity

The APE remains two practical, non-academic host-site deliverables:

1. Environmental scan with executive synthesis and annotated bibliography.
2. How-to PFAC leadership toolkit/playbook.

Supporting pages, surveillance workflows, code, dashboards, and collaboration tools are implementation infrastructure. They are not additional APE deliverables.

The APE is not represented as human-subjects research. The separate ILE may use the same evidence backbone, but the APE and ILE must be described as distinct products with distinct academic purposes.

## 2. Federal terminology

Use **CMS Patient Safety Structural Measure (PSSM), Domain 5: Patient and Family Engagement** for the federal construct. Avoid language that implies “PSSM 5” is a separate measure or that a PFAC by itself establishes successful attestation.

Every PSSM claim must be traceable to current CMS/CDC/NHSN or AHRQ material.

## 3. Evidence discipline

For each material claim, distinguish:

- requirement or guidance;
- empirical finding;
- conceptual framework;
- implementation recommendation;
- local hypothesis or proposed action;
- lived-experience perspective.

Do not convert implementation guidance, conceptual frameworks, or patient stories into causal outcome evidence.

The evidence base must show limitations and negative/uncertain findings. In particular, the project must state that rigorous evidence linking PFACs directly to patient safety, patient satisfaction, or clinical outcomes remains limited.

## 4. Environmental scan method

A faculty reviewer should be able to identify:

- search question and scope;
- databases and grey-literature sources;
- exact search strings or a reproducible search record;
- dates searched;
- inclusion and exclusion criteria;
- screening and deduplication process;
- extraction fields;
- evidence-strength or critical-appraisal approach;
- counts or a transparent status statement if screening is still in progress;
- reasons for excluding evidence that conflicts with the project thesis.

The method should minimize confirmation bias. “Supports leadership action” is not, by itself, a sufficient inclusion criterion.

## 5. Competency traceability

The two APE deliverables must visibly demonstrate all five selected competencies.

### CEPH 4
Interpret results of data analysis for public health research, policy, or practice.

Required proof: a visible analysis artifact with data source, method, results, and interpretation. Literature synthesis alone should not be labeled data analysis unless the project explicitly defines and executes a structured qualitative/documentary analysis.

### CEPH 7
Assess population needs, assets, and capacities that affect communities’ health.

Required proof: define the population or service-area context and document the needs/assets/capacities assessed, the evidence used, and the implications for PFAC design or implementation.

### CEPH 16
Apply leadership and/or management principles to address a relevant issue.

Required proof: governance, ownership, action tracking, escalation, reassessment, and accountability.

### CEPH 21
Integrate perspectives from other sectors and/or professions to promote and advance population health.

Required proof: document which perspectives were actually integrated and how they changed the product. Do not imply direct patient or stakeholder co-design where only published sources were reviewed.

### Dartmouth program-specific competency 4
Compare two approaches to engaging target populations in decision making, design, governance, and delivery of services, including implications for quality, safety, equity, and value.

Required proof: an explicit comparison using common dimensions, not a set of unrelated examples.

## 6. Patient voice and ethics

A public patient story may be used as a lived-experience design lens. It does not become research evidence and does not imply direct participation, co-design, permission, partnership, or endorsement unless those facts are documented.

Avoid tokenizing a single story or presenting it as representative of all patients. Preserve source attribution and distinguish story-derived questions from empirical findings.

## 7. Dartmouth Health claims

Publicly visible Dartmouth Health assets may support an environmental scan. Do not publish a systemwide rating, maturity score, causal conclusion, or internal operating claim without sufficient reviewed evidence.

Use status labels such as publicly supported, preliminary finding, not yet validated, and insufficient evidence. Keep framework questions separate from completed findings.

## 8. Communication quality

Faculty-facing content should be concise, neutral, professional, and evidence calibrated. Remove promotional claims such as “industry-grade,” unsupported superiority claims such as “improves on” established toolkits, brand analogies in formal evidence sections, and polemical language about payers or bureaucracy.

## 9. Technical and privacy gates

- No PHI or private patient identifiers.
- Public intake endpoints require abuse protection before production use.
- Supabase tables in exposed schemas require RLS.
- Public client code must never expose service-role or secret keys.
- Automated regression tests must protect evidence-state labels and faculty-critical language.

## Definition of faculty-ready

A page is faculty-ready only when its claims are supported, limitations are visible, APE scope is clear, competency evidence is traceable, patient voice is used ethically, and a reviewer can distinguish what is completed from what is proposed or still unvalidated.
