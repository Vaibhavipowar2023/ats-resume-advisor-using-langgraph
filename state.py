"""
State is the shared memory that flows through every node in the graph.
"""
from typing import TypedDict, List, Annotated


def keep_last(a, b):
    """
    Reducer that keeps the latest value.
    Used for fields that get replaced not appended.
    Example: current_index, job_title, final_report
    """
    return b


class ResumeState(TypedDict):
    """
    Complete state of the Resume Screener graph.
    Every field uses Annotated with keep_last reducer
    so LangGraph knows how to update each field.
    """

    # ── Inputs ────────────────────────────────────────────────
    job_description: str
    resumes:         List[dict]

    # ── JD Analysis ───────────────────────────────────────────
    job_title:           Annotated[str,       keep_last]
    required_skills:     Annotated[List[str], keep_last]
    required_experience: Annotated[str,       keep_last]
    required_education:  Annotated[str,       keep_last]

    # ── Processing ────────────────────────────────────────────
    current_index: Annotated[int, keep_last]
    total_resumes: Annotated[int, keep_last]

    # ── Results ───────────────────────────────────────────────
    all_scores:  Annotated[List[dict], keep_last]
    shortlisted: Annotated[List[dict], keep_last]
    rejected:    Annotated[List[dict], keep_last]

    # ── Final outputs ─────────────────────────────────────────
    ranked_candidates:   Annotated[List[dict], keep_last]
    interview_questions: Annotated[List[dict], keep_last]
    final_report:        Annotated[str,        keep_last]


def create_initial_state(
    job_description: str,
    resumes: List[dict],
) -> dict:
    """
    Create the initial state dict to start the graph.
    Returns a plain dict — LangGraph handles it correctly.
    """
    return {
        "job_description":     job_description,
        "resumes":             resumes,
        "job_title":           "",
        "required_skills":     [],
        "required_experience": "",
        "required_education":  "",
        "current_index":       0,
        "total_resumes":       len(resumes),
        "all_scores":          [],
        "shortlisted":         [],
        "rejected":            [],
        "ranked_candidates":   [],
        "interview_questions": [],
        "final_report":        "",
    }


if __name__ == "__main__":
    from sample_data import SAMPLE_JD, SAMPLE_RESUMES

    state = create_initial_state(SAMPLE_JD, SAMPLE_RESUMES)

    print("=" * 55)
    print("  Initial State Created")
    print("=" * 55)
    print(f"  Job description: {len(state['job_description'])} chars")
    print(f"  Total resumes:   {state['total_resumes']}")
    print(f"  Current index:   {state['current_index']}")
    print(f"  Shortlisted:     {len(state['shortlisted'])}")
    print(f"  Rejected:        {len(state['rejected'])}")
    print("\nState ready. All fields will be filled by graph nodes.")