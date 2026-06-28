from pydantic import BaseModel, Field

# pydantic (output parser)
class MilestonePlanItem(BaseModel):
    number: int
    title: str
    description: str
    backend_scope: list[str] = Field(default_factory=list)
    frontend_scope: list[str] = Field(default_factory=list)


class MilestonePlan(BaseModel):
    milestones: list[MilestonePlanItem]


class MilestoneDocumentation(BaseModel):
    title: str
    completed_features: list[str]
    pending_features: list[str]
    summary: str
