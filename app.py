import streamlit as st
from dotenv import load_dotenv

from graph import run_screener

load_dotenv()

try:
    from pypdf import PdfReader

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


st.set_page_config(
    page_title="ATS Resume Advisor",
    page_icon="📄",
    layout="wide",
)


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from an uploaded PDF."""
    if not PDF_SUPPORT:
        return "PDF support is not installed. Run `uv sync` and try again."

    try:
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text).strip()
    except Exception as exc:
        return f"Error reading PDF: {exc}"


def score_color(score: int) -> str:
    if score >= 80:
        return "#198754"
    if score >= 60:
        return "#b7791f"
    return "#dc3545"


def render_list(items: list, empty_message: str):
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.write(empty_message)


def render_score_card(title: str, score: int, help_text: str):
    color = score_color(score)
    st.markdown(
        f"""
<div style="border:1px solid #dee2e6; border-radius:8px; padding:16px;
            border-left:4px solid {color}; min-height:120px;">
    <div style="font-size:0.9rem; color:#6c757d;">{title}</div>
    <div style="font-size:2rem; font-weight:700; color:{color};">{score}/100</div>
    <div style="font-size:0.85rem; color:#495057;">{help_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def get_application_readiness(candidate: dict) -> tuple[str, str, str]:
    """Return readiness label, color, and explanation for the candidate."""
    match_score = candidate.get("score", 0)
    ats_score = candidate.get("ats_score", match_score)
    missing_skills = candidate.get("missing_skills", [])
    missing_keywords = candidate.get("missing_keywords", [])
    hard_gaps = candidate.get("rejection_reasons", [])

    critical_terms = {
        "api",
        "apis",
        "backend",
        "production",
        "production systems",
        "fastapi",
        "flask",
        "django",
        "testing",
        "clean coding",
        "clean coding practices",
    }
    missing_text = " ".join(missing_skills + missing_keywords).lower()
    has_critical_gap = any(term in missing_text for term in critical_terms)

    if hard_gaps:
        return (
            "Not ready yet",
            "#dc3545",
            "A hard JD requirement is missing.",
        )

    if match_score >= 80 and ats_score >= 80 and not has_critical_gap:
        return (
            "Ready to apply",
            "#198754",
            "Strong ATS alignment and JD match.",
        )

    if match_score >= 65 or ats_score >= 70:
        return (
            "Improve before applying",
            "#b7791f",
            "Good base, but important JD signals are missing.",
        )

    return (
        "Not ready yet",
        "#dc3545",
        "Several important JD requirements are missing.",
    )


def render_candidate_result(candidate: dict):
    match_score = candidate.get("score", 0)
    ats_score = candidate.get("ats_score", match_score)
    missing_skills = candidate.get("missing_skills", [])
    missing_keywords = candidate.get("missing_keywords", [])
    rejection_reasons = candidate.get("rejection_reasons", [])

    st.subheader("Resume Fit Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_score_card(
            "ATS Score",
            ats_score,
            "Keyword coverage, formatting signals, and JD alignment.",
        )
    with c2:
        render_score_card(
            "JD Match Score",
            match_score,
            "Overall fit between the resume and job description.",
        )
    with c3:
        readiness, color, readiness_help = get_application_readiness(candidate)
        st.markdown(
            f"""
<div style="border:1px solid #dee2e6; border-radius:8px; padding:16px;
            border-left:4px solid {color}; min-height:120px;">
    <div style="font-size:0.9rem; color:#6c757d;">Application Readiness</div>
    <div style="font-size:1.35rem; font-weight:700; color:{color}; margin-top:8px;">
        {readiness}
    </div>
    <div style="font-size:0.85rem; color:#495057; margin-top:8px;">
        {readiness_help}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    if candidate.get("summary"):
        st.info(candidate["summary"])

    if rejection_reasons:
        st.error("Hard requirement gap found: " + " ".join(rejection_reasons))

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("### What Already Matches")
        st.markdown("**Skills found in your resume**")
        render_list(candidate.get("matched_skills", []), "No matching skills found.")

        st.markdown("**ATS keywords already present**")
        render_list(candidate.get("matched_keywords", []), "No JD keywords found.")

    with right:
        st.markdown("### What Is Missing")
        st.markdown("**Missing skills**")
        render_list(missing_skills, "No major missing skills found.")

        st.markdown("**Missing ATS keywords**")
        render_list(missing_keywords, "No major missing keywords found.")

    st.divider()

    st.markdown("### JD vs Resume Gap")
    render_list(
        candidate.get("gap_analysis", []),
        "No major JD-to-resume gaps were detected.",
    )

    st.markdown("### What To Add To Improve ATS Score")
    render_list(
        candidate.get("improvement_suggestions", []),
        "No specific additions suggested.",
    )

    sections = candidate.get("resume_sections_to_add", [])
    if sections:
        st.markdown("### Suggested Resume Sections or Bullets")
        render_list(sections, "No section suggestions found.")

    st.divider()

    with st.expander("View extracted resume text"):
        st.text(candidate.get("resume", ""))


def main():
    st.title("📄 ATS Resume Advisor")
    st.caption(
        "Upload or paste your resume and a job description. "
        "The system will show your ATS score, missing gaps, and what to add before applying."
    )
    st.divider()

    if "result" not in st.session_state:
        st.session_state.result = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "jd_text" not in st.session_state:
        st.session_state.jd_text = ""

    input_tab, result_tab = st.tabs(["Input", "ATS Advice"])

    with input_tab:
        col_jd, col_resume = st.columns(2)

        with col_jd:
            st.subheader("1. Add Job Description")
            jd_method = st.radio(
                "Job description input",
                ["Paste text", "Upload PDF"],
                horizontal=True,
                key="jd_method",
            )

            if jd_method == "Upload PDF":
                jd_file = st.file_uploader(
                    "Upload JD PDF",
                    type=["pdf"],
                    key="jd_pdf",
                )
                if jd_file:
                    st.session_state.jd_text = extract_text_from_pdf(jd_file)
                    st.success(f"JD extracted: {len(st.session_state.jd_text)} characters")
            else:
                st.session_state.jd_text = st.text_area(
                    "Paste the full job description",
                    value=st.session_state.jd_text,
                    height=360,
                    placeholder="Paste the JD here...",
                )

        with col_resume:
            st.subheader("2. Add Your Resume")
            resume_method = st.radio(
                "Resume input",
                ["Upload PDF", "Paste text"],
                horizontal=True,
                key="resume_method",
            )

            candidate_name = st.text_input(
                "Your name",
                value="Candidate",
                placeholder="e.g. Vaibhav Powar",
            )

            if resume_method == "Upload PDF":
                resume_file = st.file_uploader(
                    "Upload your resume PDF",
                    type=["pdf"],
                    key="resume_pdf",
                )
                if resume_file:
                    st.session_state.resume_text = extract_text_from_pdf(resume_file)
                    if candidate_name == "Candidate":
                        candidate_name = resume_file.name.replace(".pdf", "").replace("_", " ")
                    st.success(
                        f"Resume extracted: {len(st.session_state.resume_text)} characters"
                    )
            else:
                st.session_state.resume_text = st.text_area(
                    "Paste your resume text",
                    value=st.session_state.resume_text,
                    height=310,
                    placeholder="Paste your resume here...",
                )

        st.divider()

        jd_ready = bool(st.session_state.jd_text.strip())
        resume_ready = bool(st.session_state.resume_text.strip())
        st.info(
            f"Ready status: JD {'added' if jd_ready else 'missing'} | "
            f"Resume {'added' if resume_ready else 'missing'}"
        )

        if st.button(
            "Analyze My Resume",
            type="primary",
            use_container_width=True,
            disabled=not (jd_ready and resume_ready),
        ):
            resume_payload = [
                {
                    "name": candidate_name.strip() or "Candidate",
                    "resume": st.session_state.resume_text.strip(),
                    "source": resume_method.lower(),
                }
            ]
            with st.spinner("Analyzing your resume against the JD..."):
                st.session_state.result = run_screener(
                    st.session_state.jd_text.strip(),
                    resume_payload,
                )
            st.success("Analysis complete. Open the ATS Advice tab.")

    with result_tab:
        result = st.session_state.result
        if not result:
            st.info("No analysis yet. Add your JD and resume in the Input tab.")
            return

        scores = result.get("all_scores", [])
        if not scores:
            st.error("No resume score was returned. Please try again.")
            return

        render_candidate_result(scores[0])

        report = result.get("final_report", "")
        if report:
            st.markdown("### Advisor Report")
            st.markdown(report)

        if st.button("Clear and Analyze Another Resume"):
            st.session_state.result = None
            st.session_state.resume_text = ""
            st.session_state.jd_text = ""
            st.rerun()


if __name__ == "__main__":
    main()
