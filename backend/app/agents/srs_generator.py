from app.llm.factory import get_groq_code
from app.llm.structured import invoke_structured
from app.models.planning import PlanningEstimate
from app.models.requirements import RequirementsSummary
from app.models.srs import SRSDocument

# 1- system prompt
# 2- human prompt (context)
# 3- query (input)
def run_srs_generator(
    requirements: RequirementsSummary,
    estimate: PlanningEstimate,
) -> SRSDocument:
    llm = get_groq_code()
    return invoke_structured(
        llm,
        SRSDocument,
        "Generate a concise SRS: functional/non-functional requirements, actors, modules, user flow, tech stack.",
        "Requirements:\n{requirements}\n\nEstimate:\n{estimate}",
        {
            "requirements": requirements.model_dump_json(indent=2),
            "estimate": estimate.model_dump_json(indent=2),
        },
    )
