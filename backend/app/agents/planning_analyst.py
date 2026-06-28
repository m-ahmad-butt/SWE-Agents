from app.llm.factory import get_groq_structured
from app.llm.structured import invoke_structured
from app.models.planning import PlanningEstimate
from app.models.requirements import RequirementsSummary

# 1- system prompt
# 2- human prompt (context)
# 3- query (input)
def run_planning_analyst(requirements: RequirementsSummary) -> PlanningEstimate:
    llm = get_groq_structured()
    req_text = requirements.model_dump_json(indent=2)
    estimate = invoke_structured(
        llm,
        PlanningEstimate,
        (
            "You are a Planning Analyst. Estimate timeline, team size, cost, and complexity. "
            "Rules: always at least 1 frontend developer. "
            "Use 0 backend ONLY for pure static/client-only apps (no server, no API). "
            "For most web apps use at least 1 backend developer."
        ),
        "Requirements:\n{requirements}",
        {"requirements": req_text},
    )

    # for pure frontend apps
    if estimate.backend_developers == 0:
        estimate.assumptions.append(
            "Client-only app: no server/API required; frontend engineer handles all code."
        )
    return estimate
