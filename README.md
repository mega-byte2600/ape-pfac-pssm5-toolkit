# APE PFAC PSSM 5 Leadership Toolkit

This repository is a standalone MPH Applied Practice Experience demo.

It is not connected to Hedge Desk or any finance project.

## First acknowledgement

This project is dedicated first and foremost to Rosie Bartel.

Rosie Bartel's lived experience after total knee replacement, healthcare-associated MRSA infection, sepsis, amputation, and long-term patient safety advocacy is the patient story anchor for this toolkit. Without her public witness and advocacy, this project would not have the same purpose, urgency, or moral center.

Formal research explains what the evidence supports. Rosie Bartel's story explains why the toolkit must stay patient first.

See `ACKNOWLEDGEMENT.md` and `web/story.html`.

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

## Scope boundary

This project is only for the MPH Applied Practice Experience PFAC/PSSM 5 toolkit. It must not be routed through, branded with, or mixed into Hedge Desk or any other unrelated project.
