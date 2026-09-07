"""Open data and public research resources for PFAC/PSSM 5 work."""

from __future__ import annotations


def build_open_resources():
    return [
        {
            "name": "AHRQ CMS PSSM domain resources",
            "type": "Government standard",
            "url": "https://www.ahrq.gov/action-alliance/resources/measure-domains.html",
            "description": "Public AHRQ resource page organized around the CMS Patient Safety Structural Measure domains.",
            "research_use": "Use as the PSSM 5 control source and to map PFAC structure to patient and family engagement requirements.",
        },
        {
            "name": "AHRQ Guide to Patient and Family Engagement in Hospital Quality and Safety",
            "type": "Implementation toolkit",
            "url": "https://www.ahrq.gov/patient-safety/patients-families/engagingfamilies/guide.html",
            "description": "AHRQ evidence-based guide for hospitals working with patients and families to improve quality and safety.",
            "research_use": "Use for practical PFAC deployment assets, patient-first scripts, and co-design implementation logic.",
        },
        {
            "name": "AHRQ CAHPS program",
            "type": "Survey and measurement resource",
            "url": "https://www.ahrq.gov/cahps/index.html",
            "description": "Public CAHPS program resources for assessing patient experience across care settings.",
            "research_use": "Use to align PFAC actions with validated patient experience measurement concepts.",
        },
        {
            "name": "CMS HCAHPS survey overview",
            "type": "National patient experience measure",
            "url": "https://www.cms.gov/medicare/quality/initiatives/hospital-quality-initiative/hcahps-patients-perspectives-care-survey",
            "description": "CMS overview of HCAHPS, the national standardized survey of hospital patients' perspectives of care.",
            "research_use": "Use to connect PFAC improvement work to publicly reported patient experience domains and global ratings.",
        },
        {
            "name": "CMS Provider Data Catalog: HCAHPS Hospital dataset",
            "type": "Open data API",
            "url": "https://data.cms.gov/provider-data/dataset/dgck-syfz",
            "description": "CMS open dataset with hospital-level HCAHPS patient experience ratings and API access.",
            "research_use": "Use for benchmarking hospital patient experience measures and tracking external comparison metrics.",
        },
        {
            "name": "CMS Provider Data Catalog: HCAHPS National dataset",
            "type": "Open data API",
            "url": "https://data.cms.gov/provider-data/dataset/99ue-w85f",
            "description": "CMS open national HCAHPS patient survey dataset with API access.",
            "research_use": "Use for national comparison baselines when interpreting local patient experience trends.",
        },
        {
            "name": "CDC NHSN Patient Safety Structural Measure page",
            "type": "Reporting and submission resource",
            "url": "https://www.cdc.gov/nhsn/psc/pssm.html",
            "description": "CDC NHSN page for CMS Patient Safety Structural Measure reporting resources and quick reference materials.",
            "research_use": "Use to validate reporting context and connect toolkit outputs to structural measure implementation timing.",
        },
        {
            "name": "AHRQ primary care patient and family engagement guide",
            "type": "Implementation toolkit",
            "url": "https://www.ahrq.gov/patient-safety/reports/engage.html",
            "description": "AHRQ guide for engaging patients and families in primary care safety improvement.",
            "research_use": "Use to adapt the PFAC toolkit beyond inpatient settings and support ambulatory patient experience improvement.",
        },
        {
            "name": "AHRQ Effective Health Care patient, family, and caregiver engagement framework",
            "type": "Research framework",
            "url": "https://effectivehealthcare.ahrq.gov/products/family-engagement/protocol",
            "description": "AHRQ framework covering levels of patient, family, and caregiver engagement, including PFACs and measurement concepts.",
            "research_use": "Use to structure environmental scan categories and compare engagement approaches across levels of decision-making.",
        },
        {
            "name": "PubMed PFAC and patient advisor evidence search",
            "type": "Open literature search",
            "url": "https://pubmed.ncbi.nlm.nih.gov/?term=patient+family+advisory+council+healthcare+systematic+review",
            "description": "Reusable PubMed query for peer-reviewed PFAC and patient advisor evidence.",
            "research_use": "Use to refresh the annotated bibliography and avoid relying only on static sources.",
        },
    ]
