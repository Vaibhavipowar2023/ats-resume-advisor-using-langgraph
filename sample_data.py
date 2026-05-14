"""
sample_data.py
--------------
Generates sample job description and resumes for testing.
Run this to see sample data before building the graph.

Usage:
    python sample_data.py
"""

# ── Sample Job Description ────────────────────────────────────
SAMPLE_JD = """
Job Title: Machine Learning Engineer

Company: TechCorp India Pvt Ltd
Location: Pune, Maharashtra

About the Role:
We are looking for a passionate Machine Learning Engineer
to join our AI team. You will build and deploy ML models
that power our core products.

Required Skills:
- Python programming (3+ years)
- Machine Learning (scikit-learn, TensorFlow or PyTorch)
- Natural Language Processing (NLP)
- RAG systems and LLM applications
- SQL and data manipulation
- Git version control

Good to Have:
- LangChain or LlamaIndex experience
- Cloud platforms (AWS or GCP)
- FastAPI or Flask for model deployment
- Docker and containerization

Experience: 1-3 years
Education: B.Tech/B.E in Computer Science or related field
"""

# ── Sample Resumes ────────────────────────────────────────────
SAMPLE_RESUMES = [
    {
        "name": "Priya Sharma",
        "resume": """
Name: Priya Sharma
Email: priya.sharma@email.com
Location: Pune, Maharashtra

SUMMARY:
Fresh graduate with strong ML skills and 2 internships
in machine learning and NLP projects.

SKILLS:
- Python (3 years)
- Machine Learning: scikit-learn, TensorFlow
- NLP: NLTK, spaCy, Hugging Face transformers
- RAG systems: LangChain, ChromaDB
- SQL: MySQL, PostgreSQL
- Git, GitHub

EXPERIENCE:
ML Intern — DataTech Solutions (6 months)
- Built sentiment analysis model with 89% accuracy
- Developed RAG chatbot using LangChain and OpenAI
- Worked with large datasets using pandas and numpy

NLP Intern — AI Startup (3 months)
- Text classification using BERT
- Data preprocessing pipelines

EDUCATION:
B.Tech Computer Science — Pune University (2024)
CGPA: 8.5/10

PROJECTS:
- Legal Document Q&A using RAG (LangChain + ChromaDB)
- Customer Churn Prediction (scikit-learn)
- Stock Price Prediction (LSTM)
"""
    },
    {
        "name": "Rahul Verma",
        "resume": """
Name: Rahul Verma
Email: rahul.verma@email.com
Location: Mumbai, Maharashtra

SUMMARY:
2 years experience in software development.
Interested in transitioning to ML engineering.

SKILLS:
- Python (2 years)
- Basic Machine Learning (scikit-learn only)
- Web Development: Django, React
- SQL: MySQL
- Git

EXPERIENCE:
Software Developer — WebCorp (2 years)
- Built REST APIs using Django
- Frontend development with React
- Database management with MySQL

EDUCATION:
B.Tech Computer Science — Mumbai University (2022)
CGPA: 7.2/10

PROJECTS:
- E-commerce website (Django + React)
- Todo app with authentication
"""
    },
    {
        "name": "Sneha Patel",
        "resume": """
Name: Sneha Patel
Email: sneha.patel@email.com
Location: Bangalore, Karnataka

SUMMARY:
Data Scientist with 2 years experience in ML and NLP.
Strong background in deep learning and LLM applications.

SKILLS:
- Python (4 years)
- Machine Learning: scikit-learn, XGBoost, LightGBM
- Deep Learning: PyTorch, TensorFlow
- NLP: transformers, LangChain, LlamaIndex
- RAG systems: Qdrant, Pinecone, ChromaDB
- SQL, NoSQL (MongoDB)
- AWS SageMaker, Docker
- FastAPI for model deployment
- Git, MLflow

EXPERIENCE:
Data Scientist — AI Solutions Ltd (2 years)
- Built and deployed 5 production ML models
- Developed RAG system for enterprise search
- LLM fine-tuning using LoRA
- Reduced model inference time by 40%

EDUCATION:
M.Tech Data Science — IIT Bangalore (2022)
CGPA: 9.1/10

PROJECTS:
- Multi-agent RAG system (LangGraph + LangChain)
- Medical diagnosis assistant (LLM + RAG)
- Real-time fraud detection system
"""
    },
    {
        "name": "Amit Kumar",
        "resume": """
Name: Amit Kumar
Email: amit.kumar@email.com
Location: Delhi

SUMMARY:
Fresher with strong academic background in AI/ML.
No work experience but good project portfolio.

SKILLS:
- Python (2 years)
- Machine Learning: scikit-learn
- Deep Learning: basic TensorFlow
- SQL: basic MySQL
- Git: basic

EDUCATION:
B.Tech Computer Science — Delhi University (2024)
CGPA: 6.8/10

PROJECTS:
- House price prediction (linear regression)
- Iris flower classification
- Simple chatbot using NLTK
"""
    },
    {
        "name": "Kavya Reddy",
        "resume": """
Name: Kavya Reddy
Email: kavya.reddy@email.com
Location: Hyderabad, Telangana

SUMMARY:
ML Engineer with 1.5 years experience specializing
in NLP and conversational AI systems.

SKILLS:
- Python (3 years)
- Machine Learning: scikit-learn, XGBoost
- NLP: transformers, spaCy, LangChain
- LLM Applications: GPT-4, Llama, Groq
- RAG: ChromaDB, FAISS, Qdrant
- SQL: PostgreSQL
- FastAPI, Docker
- Git, GitHub Actions

EXPERIENCE:
ML Engineer — NLP Startup (1.5 years)
- Built conversational AI for customer support
- Developed RAG pipeline for document Q&A
- LangChain agent development with tool use
- Deployed models using FastAPI and Docker

EDUCATION:
B.Tech AI/ML — JNTU Hyderabad (2022)
CGPA: 8.8/10

PROJECTS:
- Banking FAQ chatbot (RAG + LangChain)
- Resume parser using NLP
- Sentiment analysis dashboard
"""
    },
]


if __name__ == "__main__":
    print("=" * 55)
    print("  Sample Data for Resume Screener")
    print("=" * 55)

    print(f"\nJob Description:")
    print(f"  Title: Machine Learning Engineer")
    print(f"  Company: TechCorp India")

    print(f"\nResumes to screen: {len(SAMPLE_RESUMES)}")
    for i, r in enumerate(SAMPLE_RESUMES, 1):
        print(f"  {i}. {r['name']}")

    print("\nRun python graph.py to screen these resumes.")