# Evidence Closeout Report

## Purpose

Close development for faculty demo by validating the public APE's highest-risk claims, local calculations, source identifiers, and methodological boundaries against authoritative or publisher records. This report is a QA record, not a new APE deliverable.

## Local data provenance

Primary source: Dartmouth Hitchcock Medical Center, Alice Peck Day Memorial Hospital, and Visiting Nurse and Hospice for Vermont and New Hampshire. Fiscal Year 2025 Community Health Needs Assessment.

Validated source locations:

- CHNA page 1: defines the 19-municipality DHMC-APD primary service area and estimated population of 72,736.
- CHNA pages 7-8, Table 1: 2023 municipality population estimates and age 65+ percentages; service-area total 72,736 and age 65+ benchmark 22%.
- CHNA pages 8-9, Table 2: municipality poverty and disability percentages; service-area benchmarks approximately 8% poverty and 12% disability.
- CHNA page 23, Table 6: 42% primary care access difficulty, 35% mental health access difficulty; among respondents with mental health access difficulty, 68% cited long waits and 62% cited practices not accepting new patients.
- CHNA page 4 summary: community leaders/service providers identified insufficient local capacity at 72%, difficulty navigating the health care system at 59%, and isolated populations not adequately served at 55%.

The CHNA identifies the underlying demographic source as U.S. Census Bureau American Community Survey 2019-2023 5-Year Estimates.

## Independent calculation reconciliation

The public CSV contains 19 municipalities totaling 72,736 residents.

| Derived signal | Residents in municipalities above service-area benchmark | Recalculated share | Public headline |
|---|---:|---:|---:|
| Poverty > 8% | 35,234 | 48.44% | 48.4% |
| Disability > 12% | 43,995 | 60.49% | 60.5% |
| Age 65+ > 22% | 34,875 | 47.95% | 47.9% |

All three public headline calculations reconcile to the source CSV after rounding to one decimal place.

## Peer-reviewed source validation

The following core citations were checked against publisher, PubMed, or PubMed Central records for title, journal/year, article identifier/pages, and DOI.

| Source | Validation result |
|---|---|
| Lewis et al. Use of Hospital Patient and Family Advisory Councils: A Scoping Study. J Patient Exp. 2025;12:23743735251316995. | Validated. DOI 10.1177/23743735251316995. Publisher record confirms 143 articles reviewed and limited reporting of measured PFAC outcomes. |
| Lewis et al. Hospital Patient and Family Advisory Councils: A Quantitative Study on How Councils are Used and Predictors of Effective Councils. J Patient Exp. 2026;13:23743735261415786. | Validated. DOI 10.1177/23743735261415786. Publisher record confirms 203 respondents and associations between leadership support and operational practices. |
| Rramani Dervishi et al. Engaging PFACs in patient safety in healthcare organisations: a rapid scoping review. BMJ Open Qual. 2026;15(1):e004040. | Validated. DOI 10.1136/bmjoq-2025-004040. Review explicitly describes heterogeneous resources and need for stronger evidence. |
| Leia, See, Cuthbert. Barriers and Facilitators to the Recruitment and Engagement of Diverse Populations Into PFACs. J Patient Exp. 2025;12:23743735251376068. | Validated. DOI 10.1177/23743735251376068. Publisher/PubMed records confirm 43 included studies and representation barriers/facilitators. |
| Oldfield et al. Patient, Family, and Community Advisory Councils in Health Care and Research: a Systematic Review. J Gen Intern Med. 2019;34(7):1292-1303. | Validated. DOI 10.1007/s11606-018-4565-9. |
| Sharma et al. The impact of patient advisors on healthcare outcomes: a systematic review. BMC Health Serv Res. 2017;17:693. | Validated. DOI 10.1186/s12913-017-2630-4. The review notes limited evidence for attributing downstream outcomes to advisory councils. |
| Batalden et al. Coproduction of healthcare service. BMJ Qual Saf. 2016;25(7):509-517. | Validated. DOI 10.1136/bmjqs-2015-004315. |
| Batalden, Foster. From assurance to coproduction: a century of improving the quality of health-care service. Int J Qual Health Care. 2021;33(suppl 2):ii10-ii14. | Validated. DOI 10.1093/intqhc/mzab059. |
| Joseph et al. Exploring Patient Journey Mapping and the Learning Health System: Scoping Review. JMIR Hum Factors. 2023;10:e43966. | Validated. DOI 10.2196/43966. |
| Oliver, Nelson, Kerrigan. Turning Feed-forward and Feedback Processes on Patient-reported Data into Intelligent Action and Informed Decision-making. Med Care. 2019;57(suppl):S31-S37. | Validated. DOI 10.1097/MLR.0000000000001088. |
| Doyle, Lennox, Bell. A systematic review of evidence on the links between patient experience and clinical safety and effectiveness. BMJ Open. 2013;3:e001570. | Validated. DOI 10.1136/bmjopen-2012-001570. |
| Carman et al. Patient and family engagement: a framework for understanding the elements and developing interventions and policies. Health Aff (Millwood). 2013;32(2):223-231. | Validated. DOI 10.1377/hlthaff.2012.1133. |

## Federal alignment

AHRQ's current CMS Patient Safety Structural Measure resource page identifies five domains and states under Domain 5: Patient and Family Engagement that a PFAC provides input on safety. The APE therefore uses the correct construct: CMS Patient Safety Structural Measure, Domain 5: Patient and Family Engagement.

The public Dartmouth Health benchmark remains an assessment framework. It does not present an unsupported maturity score or assert local compliance where evidence has not been validated.

## Claim boundaries locked for demo

- PFAC presence is not presented as proof of improved clinical, safety, or experience outcomes.
- Association findings from observational PFAC research are not presented as causal effects.
- Local municipality percentages are descriptive planning signals, not individual-level risk estimates.
- Service-area benchmark comparisons are not validated cut points.
- Rosie Bartel is used as a lived-experience anchor, not representative or causal evidence.
- Public Dartmouth Health evidence is kept separate from unvalidated current-state findings.
- The APE and separate Integrated Learning Experience remain distinct.

## Automated protection

`tests/test_evidence_integrity.py` now locks:

1. 19-municipality denominator and 72,736 population total.
2. Recalculation of 48.4%, 60.5%, and 47.9% from the source CSV.
3. Public methodological boundary language.
4. Twelve validated core peer-reviewed DOI identifiers.
5. Prohibition on a numeric PFAC maturity score.

## Demo closeout decision

Evidence closeout status: READY FOR FACULTY DEMO, subject to the existing Faculty Review, Site Regression, production smoke, and deployment gates remaining green.
