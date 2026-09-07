"""Patient-first PFAC/PSSM 5 toolkit payload.

This module contains non-sensitive, public demonstration content for the MPH
Applied Practice Experience project. It is intentionally standalone and has no
dependency on any unrelated repository or product.
"""

from __future__ import annotations


def build_toolkit():
    return {
        "schema_version": "pfac-pssm5-toolkit-1",
        "project": {
            "name": "APE PFAC PSSM 5 Leadership Toolkit",
            "identity": "MPH Applied Practice Experience demonstration",
            "scope": "PSSM 5 Patient and Family Engagement only",
            "boundary": "Standalone project. Not connected to Hedge Desk or any finance project.",
            "motto": "Patients over payers, bureaucracy, and internal convenience.",
            "patient_first_questions": [
                "How does this benefit the patient or family?",
                "How could this hurt the patient or family if we get it wrong?",
                "Would this be acceptable if the patient were me or someone I love?",
            ],
            "service_thesis": "Move from a transactional care experience to a best-in-class patient-first experience by using PFACs, co-design, co-production, and learning health system feedback loops.",
            "supabase_edge_function": "https://vgquagonefygzgebgzyx.supabase.co/functions/v1/toolkit-status",
        },
        "competencies": [
            {
                "id": "ceph-4",
                "label": "CEPH 4",
                "agreement_text": "Interpret results of data analysis for public health research, policy, or practice.",
                "proof": "Evidence is translated into practical leadership decisions that connect PFAC work to patient experience, safety, trust, equity, and measurable action.",
                "artifact": "Evidence-to-action map with AMA 11 source layer, patient benefit, patient risk, and leadership use.",
            },
            {
                "id": "ceph-7",
                "label": "CEPH 7",
                "agreement_text": "Assess population needs, assets, and capacities that affect communities' health.",
                "proof": "The PFAC is treated as listening infrastructure for patient and family needs, care barriers, trust gaps, safety concerns, cultural context, access issues, and community assets.",
                "artifact": "Patient-first current-state assessment and PFAC recruitment criteria.",
            },
            {
                "id": "ceph-16",
                "label": "CEPH 16",
                "agreement_text": "Apply leadership and/or management principles to address a relevant issue.",
                "proof": "The toolkit gives leaders a repeatable operating model to sponsor PFAC work, assign owners, act on experience signals, and document follow-through.",
                "artifact": "Leadership deployment checklist and closed-loop action tracker.",
            },
            {
                "id": "ceph-21",
                "label": "CEPH 21",
                "agreement_text": "Integrate perspectives from other sectors and/or professions to promote and advance population health.",
                "proof": "The workflow integrates patients, families, clinicians, quality, safety, operations, patient experience, equity, and executive leadership around one patient-first loop.",
                "artifact": "Stakeholder role map and co-design meeting guide.",
            },
            {
                "id": "dartmouth-4",
                "label": "Dartmouth program-specific competency 4",
                "agreement_text": "Compare approaches to engaging target populations in decision making, design, governance, and delivery of services, including effects on quality, safety, equity, and value.",
                "proof": "The toolkit compares transactional engagement with co-designed patient-first engagement and tests both against quality, safety, equity, value, and lived experience.",
                "artifact": "Service thesis, co-design pathway, and learning health system feedback loop.",
            },
        ],
        "metric_drivers": [
            {
                "metric": "Likelihood to recommend",
                "patient_question": "Would I recommend this place to someone I love after this experience?",
                "improvement_signal": "Higher LTR when safety, teamwork, communication, compassion, and trust improve.",
                "pfac_use": "Ask PFAC members where the journey feels unsafe, fragmented, rushed, or disrespectful, then co-design fixes.",
            },
            {
                "metric": "Overall rating of care",
                "patient_question": "Did the whole experience feel coordinated, safe, respectful, and clear?",
                "improvement_signal": "Higher overall rating and reduced variation across service lines and populations.",
                "pfac_use": "Use journey mapping to identify breakdowns from access to discharge and follow-up.",
            },
            {
                "metric": "Communication and clarity",
                "patient_question": "Did people explain what was happening in plain language and check understanding?",
                "improvement_signal": "Better communication scores and fewer confusion-driven complaints or avoidable calls.",
                "pfac_use": "Co-design scripts, teach-back prompts, discharge language, and escalation pathways.",
            },
            {
                "metric": "Teamwork and coordination",
                "patient_question": "Did the team seem aligned, or did I have to carry information between people?",
                "improvement_signal": "Improved teamwork perception and safer transitions.",
                "pfac_use": "PFAC reviews handoffs, referrals, and transitions from the patient point of view.",
            },
            {
                "metric": "Safety, trust, and dignity",
                "patient_question": "Did I feel safe, respected, believed, and treated as a person?",
                "improvement_signal": "Improved perception of safety, trust, dignity, and compassion.",
                "pfac_use": "PFAC tests whether safety language and dignity behaviors match lived experience.",
            },
            {
                "metric": "Equity and access",
                "patient_question": "Who is having a worse experience, and why?",
                "improvement_signal": "Reduced disparity in experience measures across age, language, race, disability, geography, or care setting.",
                "pfac_use": "Stratify patient voice and invite PFAC members who can identify barriers not visible to leadership.",
            },
        ],
        "playbook_steps": [
            {
                "title": "Lock PSSM 5 scope",
                "leader_action": "Define the work as PSSM 5 Patient and Family Engagement only.",
                "patient_benefit": "Patient and family voice has a protected lane tied to safety and engagement.",
                "guardrail": "Prevents scope drift and compliance theater.",
                "artifact": "PSSM 5 scope statement.",
            },
            {
                "title": "Start with patient-first questions",
                "leader_action": "Every decision begins with patient benefit, patient harm risk, and loved-one test questions.",
                "patient_benefit": "Operational decisions stay grounded in what patients and families actually experience.",
                "guardrail": "Prevents bureaucracy, payer pressure, and internal convenience from becoming the default priority.",
                "artifact": "Patient-first decision screen.",
            },
            {
                "title": "Recruit for lived experience and equity",
                "leader_action": "Build PFAC membership around journey pain points, trust gaps, safety concerns, access barriers, and population diversity.",
                "patient_benefit": "Patients most affected by gaps have a voice in redesign.",
                "guardrail": "Prevents tokenism and over-reliance on the easiest voices to recruit.",
                "artifact": "Recruitment and representation checklist.",
            },
            {
                "title": "Co-design the experience standard",
                "leader_action": "Use PFAC input before implementation decisions are finalized.",
                "patient_benefit": "Patients see care designed around clarity, respect, safety, and dignity.",
                "guardrail": "Prevents after-the-fact review that cannot change the design.",
                "artifact": "Co-design meeting guide.",
            },
            {
                "title": "Run the action loop",
                "leader_action": "Assign an executive sponsor, choose actions, document decisions, and report back what changed.",
                "patient_benefit": "Patients and families see that speaking up produces visible improvement.",
                "guardrail": "Prevents feedback extraction without accountability.",
                "artifact": "You said, we did tracker.",
            },
            {
                "title": "Measure what matters",
                "leader_action": "Connect PFAC themes to LTR, overall rating, communication, teamwork, safety perception, trust, complaints, access, and equity signals.",
                "patient_benefit": "Experience metrics become early warning and improvement signals.",
                "guardrail": "Prevents chasing scores while missing what patients actually need.",
                "artifact": "Quarterly patient experience metric review.",
            },
            {
                "title": "Reassess maturity",
                "leader_action": "Review PFAC influence, leadership response time, closed-loop documentation, equity reach, and improvement evidence quarterly.",
                "patient_benefit": "The health system keeps learning instead of launching once and stopping.",
                "guardrail": "Prevents stagnant advisory structures.",
                "artifact": "PFAC maturity dashboard.",
            },
        ],
        "evidence": [
            {
                "source": "AHRQ PSSM Domain 5",
                "claim": "PSSM Domain 5 centers Patient and Family Engagement and includes PFAC input on safety.",
                "patient_benefit": "Patient and family voice is built into safety structure rather than handled only after harm or complaints.",
                "risk_if_ignored": "The organization may check a compliance box without creating a real safety or experience feedback loop.",
                "leadership_use": "Controls the demo scope and anchors the toolkit to PSSM 5 requirements.",
            },
            {
                "source": "AHRQ hospital engagement guide",
                "claim": "AHRQ frames patient and family engagement as a way for hospitals to partner with patients and families to improve quality and safety.",
                "patient_benefit": "Communication, bedside practice, discharge, and safety work can be designed with patient and family input.",
                "risk_if_ignored": "Families remain passive observers during risk, transition, communication, and safety failures.",
                "leadership_use": "Informs patient-first scripts, co-design sessions, and implementation assets.",
            },
            {
                "source": "Oldfield et al., 2019",
                "claim": "PFACs are structured mechanisms for patient, family, and community engagement in health care and research.",
                "patient_benefit": "Patient voice has a formal structure to influence policies, services, and improvement priorities.",
                "risk_if_ignored": "PFACs may become tokenistic, poorly represented, or disconnected from measurable improvement.",
                "leadership_use": "Supports governance, recruitment, representation, and documentation standards.",
            },
            {
                "source": "Sharma et al., 2017",
                "claim": "Patient advisors can affect healthcare outcomes when advisory work is linked to implementation and measurement.",
                "patient_benefit": "Feedback becomes visible change rather than a meeting note.",
                "risk_if_ignored": "Patients may be asked to share lived experience without seeing improvement.",
                "leadership_use": "Supports the action tracker and measurable patient experience improvement loop.",
            },
            {
                "source": "Batalden et al., 2016",
                "claim": "Healthcare service is co-produced through relationships and activities between professionals and the people served.",
                "patient_benefit": "Care is made safer, clearer, and more humane with patients as partners.",
                "risk_if_ignored": "Care can be technically delivered while still feeling confusing, fragmented, or disrespectful.",
                "leadership_use": "Frames PFACs as co-production infrastructure, not courtesy committees.",
            },
            {
                "source": "Oliver et al., 2019",
                "claim": "Feed-forward and feedback processes can turn patient-reported data into intelligent action and informed decision-making.",
                "patient_benefit": "What patients report is interpreted and converted into action.",
                "risk_if_ignored": "Repeated harm, confusion, delays, and distrust can become normalized.",
                "leadership_use": "Defines the learning health system loop: capture, interpret, act, document, reassess.",
            },
            {
                "source": "Press Ganey patient experience reporting",
                "claim": "Experience metrics such as likelihood to recommend, overall rating, safety perception, communication, teamwork, compassion, and shared decision-making can help leaders identify patient experience improvement opportunities.",
                "patient_benefit": "Leaders treat experience data as signals about safety, trust, dignity, and coordination.",
                "risk_if_ignored": "Experience work can become reputation management rather than care improvement.",
                "leadership_use": "Connects PFAC action to practical metric families leaders already track.",
            },
        ],
        "references": [
            "Agency for Healthcare Research and Quality. Resources by the CMS Patient Safety Structural Measure Domains. AHRQ. Accessed September 7, 2026.",
            "Agency for Healthcare Research and Quality. Guide to Patient and Family Engagement in Hospital Quality and Safety. AHRQ. Accessed September 7, 2026.",
            "Oldfield BJ, Harrison MA, Genao I, et al. Patient, family, and community advisory councils in health care and research: a systematic review. J Gen Intern Med. 2019;34(7):1292-1303. doi:10.1007/s11606-018-4565-9",
            "Sharma AE, Knox M, Mleczko VL, Olayiwola JN. The impact of patient advisors on healthcare outcomes: a systematic review. BMC Health Serv Res. 2017;17:693. doi:10.1186/s12913-017-2630-4",
            "Batalden M, Batalden P, Margolis P, et al. Coproduction of healthcare service. BMJ Qual Saf. 2016;25(7):509-517. doi:10.1136/bmjqs-2015-004315",
            "Batalden P, Foster T. From assurance to coproduction: a century of improving the quality of health-care service. Int J Qual Health Care. 2021;33(suppl 2):ii10-ii14. doi:10.1093/intqhc/mzab059",
            "Oliver BJ, Nelson EC, Kerrigan CL. Turning feed-forward and feedback processes on patient-reported data into intelligent action and informed decision-making: case studies and principles. Med Care. 2019;57(suppl 5 suppl 1):S31-S37. doi:10.1097/MLR.0000000000001088",
            "Press Ganey. Patient experience 2025: new trends and behaviors. Published 2025. Accessed September 7, 2026.",
        ],
    }
