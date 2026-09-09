from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "web" / "surveillance-method.html").read_text(encoding="utf-8")
STORY = (ROOT / "web" / "story.html").read_text(encoding="utf-8")


def test_surveillance_page_has_exact_setup_architecture():
    required = [
        "PubMed → My NCBI alert → email → Outlook rule",
        "APE_MASTER_PFAC_Inpatient_Experience_Safety",
        "APE_PFAC_Core",
        "APE_Experience_Access",
        "APE_PSSM_Structural",
        "APE_Implementation_Frameworks",
        "APE_Learning_System",
        "APE_High_Evidence",
        "APE_ALERTS_MASTER",
        "APE_ALERTS_PFAC",
        "APE_ALERTS_EXP",
        "APE_ALERTS_PSSM",
        "APE_ALERTS_IMPL",
        "APE_ALERTS_LHS",
        "APE_ALERTS_SR",
        "APE_HIGH_VALUE",
        "APE_PFAC",
        "APE_EXPERIENCE_ACCESS",
        "APE_PSSM_POLICY",
        "APE_IMPLEMENTATION",
        "Subject contains APE_MASTER_PFAC_Inpatient_Experience_Safety",
        "Stop processing more rules",
        "Send to → Collections",
        "Weekly, about 10–15 minutes",
        "Monthly validation",
        "Bolton TDI APE 27",
    ]
    for text in required:
        assert text in PAGE


def test_surveillance_page_contains_reusable_sample_pubmed_query():
    required_query_terms = [
        '"Patient Participation"[Mesh]',
        '"Patient-Centered Care"[Mesh]',
        'PFAC[tiab]',
        '"Hospitals"[Mesh]',
        'inpatient*[tiab]',
        '"Patient Safety"[Mesh]',
        'PREMs[tiab]',
        '"access to care"[tiab]',
    ]
    for term in required_query_terms:
        assert term in PAGE


def test_surveillance_routing_logic_is_preserved():
    routes = [
        ("Toolkit / intervention", "APE_IMPLEMENTATION + APE_HIGH_VALUE"),
        ("Systematic / umbrella review", "APE_HIGH_VALUE"),
        ("PFAC-specific", "APE_PFAC"),
        ("Experience / communication", "APE_EXPERIENCE_ACCESS"),
        ("Policy / governance", "APE_PSSM_POLICY"),
    ]
    for study_type, collection in routes:
        assert study_type in PAGE
        assert collection in PAGE


def test_surveillance_page_is_how_to_not_generic_tooling_pitch():
    assert "Build a literature surveillance system you can actually run every week." in PAGE
    assert "Keep the architecture. Change the topic." in PAGE
    assert "Notion-ready" not in PAGE
    assert "Starter schema" not in PAGE


def test_rosie_remains_untouched_by_surveillance_work():
    assert "Rosie Bartel’s public story keeps the human consequences of system design visible." in STORY
    assert "does not imply endorsement, participation, partnership, or authorship by Rosie Bartel" in STORY
