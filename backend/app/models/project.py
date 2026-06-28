from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field
from app.models.planning import PlanningEstimate
from app.models.requirements import RequirementsSummary
from app.models.srs import SRSDocument

# pydantic (output parser)
class ProjectPhase(str, Enum):
    REQUIREMENTS = "requirements"
    PLANNING = "planning"
    NEGOTIATION = "negotiation"
    PROPOSAL_REVIEW = "proposal_review"
    SRS_GENERATION = "srs_generation"
    MILESTONE_PLANNING = "milestone_planning"
    MILESTONE_CODING = "milestone_coding"
    MILESTONE_DOCUMENTATION = "milestone_documentation"
    MILESTONE_REVIEW = "milestone_review"
    COMPLETED = "completed"


class MilestoneStatus(str, Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REVISION = "revision"


class Milestone(BaseModel):
    number: int
    title: str
    description: str
    backend_scope: list[str] = Field(default_factory=list)
    frontend_scope: list[str] = Field(default_factory=list)
    status: MilestoneStatus = MilestoneStatus.LOCKED
    documentation: str = ""
    revision_feedback: str = ""


class ChatMessage(BaseModel):
    role: str  # user | assistant | system
    content: str
    agent: str = ""
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = ""
    initial_query: str = ""
    phase: ProjectPhase = ProjectPhase.REQUIREMENTS
    active_agent: str = "requirement_engineer"
    requirements_complete: bool = False
    proposal_accepted: bool = False
    chat_history: list[ChatMessage] = Field(default_factory=list)
    requirements: RequirementsSummary | None = None
    estimate: PlanningEstimate | None = None
    negotiated_estimate: PlanningEstimate | None = None
    srs: SRSDocument | None = None
    srs_markdown: str = ""
    milestones: list[Milestone] = Field(default_factory=list)
    current_milestone_index: int = 0
    generated_files: list[str] = Field(default_factory=list)
    last_backend_summary: str = ""
    last_frontend_summary: str = ""
    run_guide_markdown: str = ""
    status_message: str = "Waiting for your project idea..."
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_message(self, role: str, content: str, agent: str = "") -> None:
        self.chat_history.append(ChatMessage(role=role, content=content, agent=agent))
        self.touch()

    def current_milestone(self) -> Milestone | None:
        if not self.milestones or self.current_milestone_index >= len(self.milestones):
            return None
        return self.milestones[self.current_milestone_index]

    def to_public_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
