import os
import json
import re

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from prompts import(
    JD_PARSE_PROMPT,
    SCORE_PROMPT,
    QUESTIONS_PROMPT,
    REPORT_PROMPT,
)

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

def get_llm() :
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key :
        raise ValueError("GROQ_API_KEY not found")

    return ChatGroq(
        model = GROQ_MODEL,
        temperature = 0.3,
        api_key = api_key
    )

def parse_json_response(content :str) -> dict :
    "Safely parse json from LLM response"
    content = content.strip()
    if "```json" in content :
        start = content.find("```json") + 7  # why 7 : coz len(```json") == 7 so it moves pointer right after ```json
        end = content.find("```", start) # find the closing triple backtics
        content = content[start : end].strip()

        '''
        ```json
        {
        "name": "Vaibhavi"
        }
        ```
        this to :
        {
        "name": "Vaibhavi"
        }
        '''
    elif "{" in content :
        start = content.find("{")
        end = content.rfind("}") + 1
        content  = content[start : end].strip()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response was not a JSON object")
    return parsed


def as_list(value) -> list:
    """Normalize model output fields that should be lists."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, tuple):
        return list(value)
    return []


def clamp_score(value) -> int:
    """Keep scores as integers between 0 and 100."""
    try:
        score = int(float(value))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def extract_min_required_years(text: str) -> float | None:
    """Extract the minimum years of experience required by the JD."""
    if not text:
        return None

    normalized = text.lower().replace("+", "+ ")
    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*\d+(?:\.\d+)?\s*years?",
        normalized,
    )
    if range_match:
        return float(range_match.group(1))

    plus_match = re.search(r"(\d+(?:\.\d+)?)\s*\+\s*years?", normalized)
    if plus_match:
        return float(plus_match.group(1))

    year_match = re.search(
        r"(?:minimum|min|at\s*least|mandatory|must\s*have)?[^.\n]{0,40}"
        r"(\d+(?:\.\d+)?)\s*years?",
        normalized,
    )
    if year_match:
        return float(year_match.group(1))

    return None


def extract_candidate_years(text: str) -> float | None:
    """Estimate candidate experience in years from resume text and file name."""
    if not text:
        return None

    normalized = text.lower()
    candidates = []

    for value, unit in re.findall(
        r"(\d+(?:\.\d+)?)\s*(years?|yrs?|yr|months?|mos?|ms)\b",
        normalized,
    ):
        amount = float(value)
        if unit.startswith(("month", "mo")) or unit == "ms":
            candidates.append(amount / 12)
        else:
            candidates.append(amount)

    compact_months = re.findall(r"\b(\d+(?:\.\d+)?)\s*m(?:o|os|s)?\b", normalized)
    candidates.extend(float(value) / 12 for value in compact_months)

    if "fresher" in normalized or "fresh graduate" in normalized:
        candidates.append(0)

    return max(candidates) if candidates else None


def apply_hard_requirement_gates(candidate_score: dict, state: dict, resume_data: dict) -> dict:
    """Prevent mandatory JD requirements from being bypassed by semantic score."""
    jd_text = " ".join(
        [
            state.get("job_description", ""),
            state.get("required_experience", ""),
        ]
    )
    resume_text = " ".join(
        [
            resume_data.get("name", ""),
            resume_data.get("resume", ""),
        ]
    )

    min_years = extract_min_required_years(jd_text)
    candidate_years = extract_candidate_years(resume_text)

    if min_years is None or candidate_years is None:
        return candidate_score

    if candidate_years < min_years:
        reason = (
            f"Experience requirement not met: JD requires at least "
            f"{min_years:g} years, resume shows about {candidate_years:g} years."
        )
        candidate_score["experience_match"] = False
        candidate_score["score"] = min(candidate_score.get("score", 0), 59)
        candidate_score["ats_score"] = min(candidate_score.get("ats_score", 0), 59)
        candidate_score["decision"] = "REJECTED"
        candidate_score.setdefault("rejection_reasons", []).append(reason)
        candidate_score.setdefault("gap_analysis", []).insert(0, reason)
        candidate_score.setdefault("improvement_suggestions", []).insert(
            0,
            "Do not apply as a 3-7 year profile until the resume shows the required professional experience.",
        )

    return candidate_score


def apply_critical_gap_caps(candidate_score: dict) -> dict:
    """Lower optimistic scores when core JD signals are missing."""
    missing_items = (
        candidate_score.get("missing_skills", [])
        + candidate_score.get("missing_keywords", [])
        + candidate_score.get("gap_analysis", [])
    )
    missing_text = " ".join(missing_items).lower()

    critical_terms = [
        "api",
        "apis",
        "backend",
        "production system",
        "production systems",
        "fastapi",
        "flask",
        "django",
        "testing",
        "clean coding",
        "clean coding practices",
    ]
    critical_hits = [term for term in critical_terms if term in missing_text]

    if len(critical_hits) >= 2:
        candidate_score["score"] = min(candidate_score.get("score", 0), 74)
        candidate_score["ats_score"] = min(candidate_score.get("ats_score", 0), 74)
        candidate_score.setdefault("gap_analysis", []).insert(
            0,
            "Core must-have signals are missing or not explicit enough for this JD.",
        )
    elif critical_hits:
        candidate_score["ats_score"] = min(candidate_score.get("ats_score", 0), 79)

    if candidate_score.get("score", 0) < 60:
        candidate_score["decision"] = "REJECTED"
    else:
        candidate_score["decision"] = "SHORTLISTED"

    return candidate_score


def parse_jd_node(state : dict) -> dict :
    """Extract requirements from the jd """
    print("\n Node 1 : Parsing Job Description : ")
    llm = get_llm()

    try :
        prompt = JD_PARSE_PROMPT.format(jd = state["job_description"])
        response = llm.invoke(prompt)
        parsed = parse_json_response(response.content)

        print(f" Job Title : {parsed.get('job_title', 'Unknown')}") # it tries to get value of key "job title" from dictionary  if key doesn't exist instead of gives error it just return "Unknown"
        print(f" Skills found : {len(parsed.get('required_skills', []))}") # This count the number of skills and get the list of skills. if skills are missing it returns empty list
        print(f" Experience : {parsed.get('required_experience' , 'N/A')}") # It gets experience value if not available it will print "N/A"
        '''
        parsed = {
        "job_title": "ML Engineer",
        "required_skills": ["Python", "TensorFlow"],
        "required_experience": "3 years"
        } 
        o/p :
        Job Title:    ML Engineer
        Skills found: 2
        Experience:   3 years
        '''

        return {
            "job_title": parsed.get("job_title", "Unknown"),
            "required_skills": parsed.get("required_skills", []),
            "required_experience": parsed.get("required_experience", ""),
            "required_education": parsed.get("required_education", ""),
        }

    except Exception as e:
        print(f"  JD parsing failed: {e}")
        return {
            "job_title": "Unknown",
            "required_skills": [],
            "required_experience": "",
            "required_education": "",
        }

def score_resume_node(state : dict) -> dict :
    """Scores the current resume against the JD."""
    index = state["current_index"]
    resume_data = state["resumes"][index]

    print(f"Node 2 : Scoring resume {index + 1} / {state['total_resumes']} :" f"{resume_data['name']}...")

    llm = get_llm()

    try :
        prompt = SCORE_PROMPT.format(
            jd = state["job_description"],
            resume = resume_data["resume"],
            required_skills = ", ".join(state["required_skills"]),
        )
        response = llm.invoke(prompt)
        scored = parse_json_response(response.content)

        score = clamp_score(scored.get("score", 0))
        ats_score = clamp_score(scored.get("ats_score", score))
        print(f" Score : {score}/ 100")
        print(f" Matched : {scored.get('matched_skills', [])}")
        print(f" Missing : {scored.get('missing_skills', [])}")

        candidate_score = {
            "name": resume_data["name"],
            "score": score,
            "ats_score": ats_score,
            "matched_skills": as_list(scored.get("matched_skills", [])),
            "missing_skills": as_list(scored.get("missing_skills", [])),
            "matched_keywords": as_list(scored.get("matched_keywords", [])),
            "missing_keywords": as_list(scored.get("missing_keywords", [])),
            "experience_match": scored.get("experience_match", False),
            "education_match": scored.get("education_match", False),
            "gap_analysis": as_list(scored.get("gap_analysis", [])),
            "improvement_suggestions": as_list(scored.get("improvement_suggestions", [])),
            "resume_sections_to_add": as_list(scored.get("resume_sections_to_add", [])),
            "summary": scored.get("summary", ""),
            "decision": "SHORTLISTED" if score >= 60 else "REJECTED",
            "rejection_reasons": [],
            "resume": resume_data["resume"],
        }
        candidate_score = apply_hard_requirement_gates(
            candidate_score,
            state,
            resume_data,
        )
        candidate_score = apply_critical_gap_caps(candidate_score)

        all_scores = state.get("all_scores", [])
        all_scores.append(candidate_score)
        return {"all_scores": all_scores}

    except Exception as e :
        print(f"  Scoring failed: {e}")
        all_scores = state.get("all_scores", [])
        all_scores.append({
            "name": resume_data["name"],
            "score": 0,
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "matched_keywords": [],
            "missing_keywords": [],
            "experience_match": False,
            "education_match": False,
            "gap_analysis": [f"Scoring failed: {e}"],
            "improvement_suggestions": ["Check the resume text extraction and run screening again."],
            "resume_sections_to_add": [],
            "summary": f"Scoring failed: {e}",
            "decision": "REJECTED",
            "rejection_reasons": [f"Scoring failed: {e}"],
            "resume": resume_data["resume"],
        })
        return {"all_scores": all_scores}


def route_decision_node(state : dict) -> dict :
    """Routes latest resume to shortlist or reject."""
    all_scores = state.get("all_scores", [])  # Get "all_scores" from dictionary state, if key does not exist use empty list []
    latest = all_scores[-1] if all_scores else None  # it returns last score in list list
    shortlisted = state.get("shortlisted" , []) #Gets shortlisted candidates
    rejected = state.get("rejected", []) # Gets rejected candidates

    if latest :
        if latest["score"] >= 60 :
            shortlisted.append(latest)
            print(f"  → SHORTLISTED: {latest['name']} ({latest['score']}/100)")

        else :
            rejected.append(latest)
            print(f"  → REJECTED: {latest['name']} ({latest['score']}/100)")


    return {
        "shortlisted" : shortlisted,
        "rejected" : rejected,
        "current_index" : state["current_index"] + 1,
    }

def rank_node(state : dict) -> dict :
    """Rank all shortlisted candidates by score."""
    print("\n Node 4 : Ranking shortlisted candidates...")

    shortlisted = state.get("shortlisted", [])
    ranked = sorted(
        shortlisted,
        key = lambda x: x["score"],
        reverse = True,
    )
    print(f"  Ranked {len(ranked)} candidates:")
    for i, c in enumerate(ranked, 1):
        print(f"  {i}. {c['name']} — {c['score']}/100")

    return {"ranked_candidates": ranked}

def generate_questions_node(state : dict) -> dict :
    """Generates interview questions for top candidates."""

    llm = get_llm()
    ranked = state.get("ranked_candidates", [])
    all_questions = []

    for candidate in ranked[:3] :
        print(f" Generating questions for {candidate['name']}...")
        try :
            prompt = QUESTIONS_PROMPT.format(
                jd = state["job_description"],
                resume = candidate.get("resume", ""),
                score = candidate["score"],
                matched_skills = candidate["matched_skills"],
                missing_skills = candidate["missing_skills"],
            )

            response = llm.invoke(prompt)
            parsed = parse_json_response(response.content)

            all_questions.append({
                "candidate_name": candidate["name"],
                "questions": parsed.get("questions", []),
                "focus_areas": parsed.get("focus_areas", []),
            })

        except Exception as e:
            print(f"  Failed for {candidate['name']}: {e}")
            all_questions.append({
                "candidate_name": candidate["name"],
                "questions": ["Tell me about your ML experience."],
                "focus_areas": ["General ML knowledge"],
            })
    return {"interview_questions": all_questions}

def report_node(state : dict) -> dict :
    """Generates the final candidate-facing resume advice report."""
    print("\n Node 6 Generating final report....")

    llm = get_llm()
    ranked = state.get("ranked_candidates", [])

    ranked_text = ""
    for i, c in enumerate(ranked, 1) :
        ranked_text += (
            f"Candidate: {c['name']}\n"
            f"   Match Score: {c['score']}/100\n"
            f"   ATS Score: {c.get('ats_score', c['score'])}/100\n"
            f"   Matched: {', '.join(c['matched_skills'][:3])}\n"
            f"   Missing: {', '.join(c['missing_skills'][:3])}\n"
            f"   Missing ATS Keywords: {', '.join(c.get('missing_keywords', [])[:5])}\n"
            f"   Main Gaps: {'; '.join(c.get('gap_analysis', [])[:3])}\n"
            f"   Suggestions: {'; '.join(c.get('improvement_suggestions', [])[:3])}\n"
            f"   Summary: {c['summary']}\n\n"
        )

    if not ranked_text:
        for c in state.get("all_scores", []):
            ranked_text += (
                f"Candidate: {c['name']}\n"
                f"   Match Score: {c['score']}/100\n"
                f"   ATS Score: {c.get('ats_score', c['score'])}/100\n"
                f"   Missing: {', '.join(c.get('missing_skills', [])[:5])}\n"
                f"   Missing ATS Keywords: {', '.join(c.get('missing_keywords', [])[:5])}\n"
                f"   Main Gaps: {'; '.join(c.get('gap_analysis', [])[:4])}\n"
                f"   Suggestions: {'; '.join(c.get('improvement_suggestions', [])[:4])}\n"
                f"   Summary: {c.get('summary', '')}\n\n"
            )

    try :
        prompt = REPORT_PROMPT.format(
                job_title=state.get("job_title", "Unknown"),
                total=state["total_resumes"],
                shortlisted_count=len(state.get("shortlisted", [])),
                rejected_count=len(state.get("rejected", [])),
                ranked_candidates=ranked_text,
            )
        response = llm.invoke(prompt)
        report = response.content.strip()

    except Exception as e :
        report = f"Report generation failed : {e}"

    print(" Report generated successfully.")
    return {"final_report" : report}

def should_continue(state : dict) :
    """
    Conditional edge function.
    Decides whether to process more resumes or rank.
    """
    current = state["current_index"]
    total = state["total_resumes"]

    if current < total :
        print(f"\n More resumes : {current} / {total}")
        return "score_resume"
    else :
        print(f"\n All {total} resumes done. Moving to ranking")
        return "rank"


if __name__ == "__main__" :
    from sample_data import SAMPLE_JD, SAMPLE_RESUMES
    from state import create_initial_state

    state = create_initial_state(SAMPLE_JD, SAMPLE_RESUMES)
    result = parse_jd_node(state)

    print("\nJD Parsing Result:")
    print(f"  Title:      {result['job_title']}")
    print(f"  Skills:     {result['required_skills']}")
    print(f"  Experience: {result['required_experience']}")
    print(f"  Education:  {result['required_education']}")


