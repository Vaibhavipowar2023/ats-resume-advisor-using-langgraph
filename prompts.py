from langchain.prompts import PromptTemplate


JD_PARSE_PROMPT = PromptTemplate(
    input_variables=["jd"],
    template="""You are an HR expert. Extract key requirements from this job description.

Job Description:
{jd}

Return ONLY a JSON object:
{{
    "job_title": "exact job title",
    "required_skills": ["skill1", "skill2", "skill3"],
    "required_experience": "e.g. 1-3 years",
    "required_education": "e.g. B.Tech Computer Science"
}}

JSON:""",
)


SCORE_PROMPT = PromptTemplate(
    input_variables=["jd", "resume", "required_skills"],
    template="""You are an expert HR recruiter and ATS resume analyst.
Score this resume against the job description and produce an ATS gap analysis.

Job Description:
{jd}

Required Skills:
{required_skills}

Resume:
{resume}

Return ONLY a JSON object:
{{
    "score": number from 0 to 100,
    "ats_score": number from 0 to 100,
    "matched_skills": ["skills that match JD"],
    "missing_skills": ["important skills missing"],
    "matched_keywords": ["important JD keywords found in resume"],
    "missing_keywords": ["important ATS/JD keywords missing from resume"],
    "experience_match": true or false,
    "education_match": true or false,
    "gap_analysis": ["specific gap between JD and resume"],
    "improvement_suggestions": ["specific suggestion to improve this resume for the JD"],
    "resume_sections_to_add": ["section or bullet the candidate should add"],
    "summary": "one sentence assessment"
}}

Scoring guide:
- 80-100: Excellent match - strong hire
- 60-79: Good match - worth interviewing
- 40-59: Partial match - missing key skills
- 0-39: Poor match - does not meet requirements

ATS guidance:
- ats_score should focus on keyword coverage, relevant job titles, skill wording,
  experience alignment, education alignment, and measurable impact bullets.
- missing_keywords should come from the JD or close synonyms.
- gap_analysis should explain the difference between what the JD asks for and
  what the resume proves.
- improvement_suggestions must be truthful and actionable. Do not suggest adding
  skills or experience the resume does not support. Suggest wording, projects,
  metrics, tools, or sections that would honestly improve ATS alignment.

JSON:""",
)


QUESTIONS_PROMPT = PromptTemplate(
    input_variables=[
        "jd",
        "resume",
        "score",
        "matched_skills",
        "missing_skills",
    ],
    template="""You are an expert technical interviewer.
Generate 5 interview questions for this candidate.

Job Description:
{jd}

Candidate Resume:
{resume}

Match Score: {score}/100
Matched Skills: {matched_skills}
Missing Skills: {missing_skills}

Generate questions that:
- Test their matched skills deeply
- Probe their missing skills gently
- Include one behavioral question
- Are specific to their experience

Return ONLY a JSON object:
{{
    "questions": [
        "question 1",
        "question 2",
        "question 3",
        "question 4",
        "question 5"
    ],
    "focus_areas": ["area1", "area2", "area3"]
}}

JSON:""",
)


REPORT_PROMPT = PromptTemplate(
    input_variables=[
        "job_title",
        "total",
        "shortlisted_count",
        "rejected_count",
        "ranked_candidates",
    ],
    template="""You are an ATS resume advisor helping a candidate improve their resume.
Write a concise candidate-facing resume improvement report.

Target Position: {job_title}
Resumes Analyzed: {total}

Resume Analysis:
{ranked_candidates}

Write a clear report with:
1. Overall ATS readiness
2. Biggest JD-to-resume gaps
3. Keywords and skills the candidate should add if truthful
4. Resume sections or bullets to improve before applying
5. Final apply/not-yet recommendation

Keep it practical, honest, and candidate-facing.""",
)


if __name__ == "__main__":
    print("=" * 55)
    print("  Resume Screener - Prompts")
    print("=" * 55)
    print(f"\n  JD Parse Prompt variables:  {JD_PARSE_PROMPT.input_variables}")
    print(f"  Score Prompt variables:     {SCORE_PROMPT.input_variables}")
    print(f"  Questions Prompt variables: {QUESTIONS_PROMPT.input_variables}")
    print(f"  Report Prompt variables:    {REPORT_PROMPT.input_variables}")
    print("\n  All prompts loaded successfully.")
