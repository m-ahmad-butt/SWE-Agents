from app.llm.factory import get_groq_structured
from app.llm.structured import invoke_structured
from app.models.milestone_doc import MilestonePlan
from app.models.project import Milestone, MilestoneStatus
from app.models.srs import SRSDocument

def run_project_manager(srs: SRSDocument) -> list[Milestone]:
    llm = get_groq_structured()
    plan: MilestonePlan = invoke_structured(
        llm,
        MilestonePlan,
        "Split the SRS into exactly 3 milestones with backend and frontend scope lists.",
        "SRS:\n{srs}",
        {"srs": srs.to_markdown()},
    )
# {"number": 1, "title": "Milestone 1", "description": "Milestone 1 description", "backend_scope": ["Backend scope 1"], "frontend_scope": ["Frontend scope 1"], "status": "IN_PROGRESS"}
# {"number": 2, "title": "Milestone 2", "description": "Milestone 2 description", "backend_scope": ["Backend scope 2"], "frontend_scope": ["Frontend scope 2"], "status": "LOCKED"}
# {"number": 3, "title": "Milestone 3", "description": "Milestone 3 description", "backend_scope": ["Backend scope 3"], "frontend_scope": ["Frontend scope 3"], "status": "LOCKED"}
    milestones: list[Milestone] = []
    for i, item in enumerate(plan.milestones):
        status = MilestoneStatus.IN_PROGRESS if i == 0 else MilestoneStatus.LOCKED
        milestones.append(
            Milestone(
                number=item.number,
                title=item.title,
                description=item.description,
                backend_scope=item.backend_scope,
                frontend_scope=item.frontend_scope,
                status=status,
            )
        )
    return milestones
