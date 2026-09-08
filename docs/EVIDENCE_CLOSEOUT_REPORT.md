# Evidence Closeout Report

## Purpose

This QA record closes development for faculty demo by validating the APE's highest-risk public claims, local calculations, source identifiers, and methodological boundaries. It is not a new APE deliverable.

## Local data provenance

Primary source: Dartmouth Hitchcock Medical Center, Alice Peck Day Memorial Hospital, and Visiting Nurse and Hospice for Vermont and New Hampshire. Fiscal Year 2025 Community Health Needs Assessment.

Validated source locations:

- Page 1: 19-municipality DHMC-APD primary service area; estimated population 72,736.
- Pages 7-8, Table 1: municipality populations and age 65+ percentages; service-area benchmark 22%.
- Pages 8-9, Table 2: municipality poverty and disability percentages; service-area benchmarks about 8% and 12%.
- Page 23, Table 6: 42% primary-care access difficulty; 35% mental-health access difficulty; among those with mental-health access difficulty, 68% cited long waits and 62% cited practices not accepting new patients.
- Page 4: 72% insufficient local capacity; 59% difficulty navigating the health care system; 55% isolated populations not adequately served.

The CHNA identifies U.S. Census Bureau American Community Survey 2019-2023 5-Year Estimates as the demographic source.

## Calculation reconciliation

The public CSV contains 19 municipalities totaling 72,736 residents.

| Signal | Residents above benchmark | Recalculated share | Public headline |
|---|---:|---:|---:|
| Poverty > 8% | 35,234 | 48.44% | 48.4% |
| Disability > 12% | 43,995 | 60.49% | 60.5% |
| Age 65+ > 22% | 34,875 | 47.95% | 47.9% |

All three headline calculations reconcile to the CSV after rounding to one decimal place.

## Peer-reviewed citation validation

The following core records were checked against publisher, PubMed, or PubMed Central metadata for title, year, journal, article identifier/pages, and DOI:

1. Lewis et al. J Patient Exp. 2025. DOI 10.1177/23743735251316995.
2. Lewis et al. J Patient Exp. 2026. DOI 10.1177/23743735261415786.
3. Rramani Dervishi et al. BMJ Open Qual. 2026. DOI 10.1136/bmjoq-2025-004040.
4. Leia, See, Cuthbert. J Patient Exp. 2025. DOI 10.1177/23743735251376068.
5. Oldfield et al. J Gen Intern Med. 2019. DOI 10.1007/s11606-018-4565-9.
6. Sharma et al. BMC Health Serv Res. 2017. DOI 10.1186/s12913-017-2630-4.
7. Batalden et al. BMJ Qual Saf. 2016. DOI 10.1136/bmjqs-2015-004315.
8. Batalden, Foster. Int J Qual Health Care. 2021. DOI 10.1093/intqhc/mzab059.
9. Joseph et al. JMIR Hum Factors. 2023. DOI 10.2196/43966.
10. Oliver, Nelson, Kerrigan. Med Care. 2019. DOI 10.1097/MLR.0000000000001088.
11. Doyle, Lennox, Bell. BMJ Open. 2013. DOI 10.1136/bmjopen-2012-001570.
12. Carman et al. Health Aff (Millwood). 2013. DOI 10.1377/hlthaff.2012.1133.

## Federal alignment

AHRQ's CMS Patient Safety Structural Measure resource identifies Domain 5 as Patient and Family Engagement and includes PFAC input on safety. The APE uses that construct correctly.

## Claim boundaries locked for demo

PFAC presence is not presented as proof of improved downstream outcomes. Observational associations are not presented as causal effects. Local municipality percentages remain descriptive planning signals, not individual-level risk estimates or validated cut points. Rosie Bartel remains a lived-experience anchor rather than representative evidence. Public Dartmouth Health evidence remains separate from unvalidated current-state findings. The APE remains distinct from the separate Integrated Learning Experience.

## Automated protection

`tests/test_evidence_integrity.py` locks the 19-municipality denominator, all three headline calculations, methodological boundary language, twelve validated DOI identifiers, and the prohibition on unsupported numeric PFAC maturity scoring.

## Demo decision

READY FOR FACULTY DEMO if Faculty Review, Site Regression, production smoke, and deployment verification remain green.
