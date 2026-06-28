import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

DATA_DIR = ROOT_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
GENERATED_DIR = DATA_DIR / "generated"
CHROMA_DIR = DATA_DIR / "chroma"
EXPORTS_DIR = DATA_DIR / "exports"

for d in (PROJECTS_DIR, GENERATED_DIR, CHROMA_DIR, EXPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Groq models (see groq.txt)
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
GROQ_STRUCTURED_MODEL = os.getenv("GROQ_STRUCTURED_MODEL", "openai/gpt-oss-20b")
GROQ_CODE_MODEL = os.getenv("GROQ_CODE_MODEL", "llama-3.3-70b-versatile")
GROQ_DOC_MODEL = os.getenv("GROQ_DOC_MODEL", "openai/gpt-oss-20b")

AGENT_PIPELINE = [
    "requirement_engineer",
    "planning_analyst",
    "negotiation_agent",
    "srs_generator",
    "project_manager",
    "backend_engineer",
    "frontend_engineer",
    "documentation_agent",
    "customer_review",
]

PHASES = [
    "requirements",
    "planning",
    "negotiation",
    "proposal_review",
    "srs_generation",
    "milestone_planning",
    "milestone_coding",
    "milestone_documentation",
    "milestone_review",
    "completed",
]
