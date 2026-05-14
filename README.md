# ATS Resume Advisor using LangGraph

An AI-powered resume improvement tool that helps candidates compare their resume against a job description and understand what to improve before applying.

The app analyzes a resume and JD, then returns an ATS score, JD match score, missing skills, missing keywords, resume gaps, and practical suggestions for improving the resume.

## Features

- Upload or paste a job description
- Upload or paste a resume
- Extract text from PDF resumes and JD files
- Generate ATS score and JD match score
- Identify matched skills and keywords
- Identify missing skills and ATS keywords
- Detect JD vs resume gaps
- Suggest what to add or improve in the resume
- Apply hard requirement checks, such as minimum years of experience
- Generate a candidate-facing resume improvement report

## Tech Stack

- Python 3.11
- Streamlit
- LangGraph
- LangChain
- Groq LLM API
- pypdf

## Project Structure

```text
.
├── app.py              # Streamlit candidate-facing app
├── graph.py            # LangGraph workflow
├── nodes.py            # Graph nodes and scoring logic
├── prompts.py          # LLM prompts
├── state.py            # Shared LangGraph state
├── sample_data.py      # Sample JD and resumes
├── pyproject.toml      # Project dependencies
├── uv.lock             # Locked dependencies
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ats-resume-advisor-langgraph.git
cd ats-resume-advisor-langgraph
```

### 2. Create and sync the virtual environment

This project uses `uv`.

```bash
uv sync
```

### 3. Add environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do not commit `.env` to GitHub.

### 4. Run the app

```bash
uv run streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## How It Works

1. The candidate adds a job description by pasting text or uploading a PDF.
2. The candidate adds their resume by pasting text or uploading a PDF.
3. LangGraph runs a resume analysis workflow:
   - Parse the job description
   - Score the resume against the JD
   - Detect missing skills and keywords
   - Apply hard requirement checks
   - Generate improvement suggestions
   - Produce a candidate-facing advisor report
4. The Streamlit UI shows the final ATS advice.

## Output Includes

- ATS Score
- JD Match Score
- Application Readiness
- Skills already matching the JD
- ATS keywords already present
- Missing skills
- Missing ATS keywords
- JD vs resume gap analysis
- Suggestions to improve the resume
- Suggested resume sections or bullet points
- Final advisor report


