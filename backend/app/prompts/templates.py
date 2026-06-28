from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# list of msgs -> dynamic prompt beacuse i need history of chats -> list of chats
REQUIREMENT_ENGINEER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Requirement Engineer at a software company.
Ask clear follow-up questions to gather requirements for the client's project.
Cover: platform (web/mobile/desktop), key features, users, constraints.
Ask ONE question at a time. Be friendly and professional.
When you have enough information (platform, 3+ features, target users), call mark_requirements_complete with a summary.""",
    ),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

NEGOTIATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Negotiation Agent. Help the client agree on budget and timeline.
Current estimate: {estimate_json}
Propose trade-offs (remove modules, phased delivery) if budget is tight.
When client agrees, call accept_proposal.""",
    ),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

PLANNING_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a Planning Analyst. Estimate timeline, team size, cost, and complexity from requirements.",
    ),
    ("human", "Requirements:\n{requirements}"),
])

SRS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Generate a concise SRS: functional/non-functional requirements, actors, modules, user flow, tech stack.",
    ),
    ("human", "Requirements:\n{requirements}\n\nNegotiated estimate:\n{estimate}"),
])

PM_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a Project Manager. Split the SRS into 3 milestones with backend and frontend scope lists.",
    ),
    ("human", "SRS:\n{srs}"),
])

BACKEND_ENGINEER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Backend Engineer. Generate FastAPI Python scaffold code for the current milestone.
Use write_code_file for each file. Paths under backend/ e.g. backend/main.py, backend/routes/auth.py.
Keep code simple and runnable. Match the SRS and milestone scope.""",
    ),
    ("human", """Milestone: {milestone_title}
Scope: {backend_scope}
SRS excerpt: {srs_excerpt}
RAG context: {rag_context}
Existing files: {existing_files}
Revision feedback: {revision_feedback}"""),
])

FRONTEND_ENGINEER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Frontend Engineer. Generate React TypeScript scaffold for the current milestone.
Use write_code_file for each file. Paths under frontend/src/ e.g. frontend/src/pages/Login.tsx.
Keep code simple. Match SRS and milestone scope.""",
    ),
    ("human", """Milestone: {milestone_title}
Scope: {frontend_scope}
SRS excerpt: {srs_excerpt}
RAG context: {rag_context}
Existing files: {existing_files}
Revision feedback: {revision_feedback}"""),
])

DOCUMENTATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a Documentation Agent. Write milestone documentation: completed features, pending items, file list.",
    ),
    ("human", """Milestone: {milestone_title}
Generated files: {generated_files}
RAG context: {rag_context}
Backend summary: {backend_summary}
Frontend summary: {frontend_summary}"""),
])

MILESTONE_LIST_SCHEMA = """Return JSON with milestones array, each having:
number, title, description, backend_scope (list), frontend_scope (list)"""
