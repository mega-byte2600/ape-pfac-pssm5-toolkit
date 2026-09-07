# APE PFAC PSSM 5 Leadership Toolkit

This repository is a standalone MPH Applied Practice Experience demo.

It is not connected to Hedge Desk or any finance project.

## First acknowledgement and patient story anchor

Rosie Bartel is the most important acknowledgement and lived-experience source for this project.

Her story is the reason this toolkit stays patient-first. Public sources describe Rosie as a Wisconsin patient advocate and sepsis survivor whose routine total knee replacement was complicated by MRSA infection, repeated surgeries, hospitalizations, transfusions, amputation, and ongoing advocacy.

The selected project anchor is:

> What matters to a patient is to survive and to survive it with some dignity and respect.

This project uses that lived-experience anchor as a design test:

Would this process be safe enough for my mother before, during, and after total knee replacement?

Would the patient or family know when to escalate infection warning signs?

Would staff listen if the patient or family said something was wrong?

Would the health system learn fast enough to protect the next patient?

## Purpose

Build an industry-grade, evidence-based leadership toolkit that helps health systems deploy Patient and Family Advisory Councils as a practical structure for CMS PSSM 5 Patient and Family Engagement.

The toolkit is designed to help leaders improve patient experience metrics, including Press Ganey-style signals such as likelihood to recommend, overall rating, communication, teamwork, safety perception, trust, dignity, access, and equity.

## Patient-first motto

Patients over payers, bureaucracy, internal convenience, and checkbox compliance.

Every design decision begins with three questions:

1. How does this benefit the patient or family?
2. How could this hurt the patient or family if we get it wrong?
3. Would this be acceptable if the patient were me, my mother, or someone I love?

## APE competency proof

This demo is built to show practical attainment of the five competencies selected in the APE Agreement:

1. CEPH 4: interpret evidence for public health research, policy, or practice.
2. CEPH 7: assess population needs, assets, and capacities.
3. CEPH 16: apply leadership and management principles.
4. CEPH 21: integrate perspectives from other sectors and professions.
5. Dartmouth program-specific competency 4: compare engagement approaches in decision making, design, governance, and service delivery, including effects on quality, safety, equity, and value.

## Comparative toolkit scan

The project now includes a comparative scan of existing PFAC and patient/family engagement toolkits from AHRQ, IPFCC, AMA STEPS Forward, Betsy Lehman Center, academic medical center projects, and learning health system literature.

The design conclusion is clear: existing toolkits are useful, but this APE product should improve on them by adding PSSM 5 traceability, Press Ganey-style patient experience metric logic, a Rosie Bartel lived-experience anchor, and a leadership action loop with visible follow-through.

## Open resources

This project includes an open resources layer so Dartmouth Health and other researchers can reuse, validate, benchmark, and improve the work.

## Architecture

- Python standard-library web service
- Static website front end
- JSON API routes
- Separate Supabase project: `ape-pfac-pssm5-toolkit`
- Separate Render service target: `ape-pfac-pssm5-toolkit`

## Local run

```bash
pip install .
pssm5-toolkit-web
```

Open `http://localhost:8765`.

## API routes

- `/api/health`
- `/api/toolkit`
- `/api/open-resources`

## Key project files

- `ACKNOWLEDGEMENT.md`
- `docs/ROSIE_BARTEL_STORY_ANCHOR.md`
- `docs/ROSIE_BARTEL_EXCERPT_SELECTION.md`
- `docs/COMPARATIVE_TOOLKIT_SCAN.md`
- `bibliography/APE_PFAC_PSSM5_BIBLIOGRAPHY.rtf`
- `web/story.html`
- `web/resources.html`

## Scope boundary

This project is only for the MPH Applied Practice Experience PFAC/PSSM 5 toolkit. It must not be routed through, branded with, or mixed into Hedge Desk or any other unrelated project.
