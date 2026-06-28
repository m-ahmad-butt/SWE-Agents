from pydantic import BaseModel, Field, field_validator

# pydantic (output parser)
class PlanningEstimate(BaseModel):
    timeline_months: int = Field(description="Estimated duration in months", ge=1)
    backend_developers: int = Field(default=1, ge=0)
    frontend_developers: int = Field(default=1, ge=1)
    estimated_cost_usd: int = Field(description="Total estimated cost in USD", ge=0)
    complexity: str = Field(description="Low, Medium, or High")
    assumptions: list[str] = Field(default_factory=list)
    module_breakdown: list[str] = Field(default_factory=list)

    @field_validator("backend_developers")
    @classmethod
    def normalize_backend(cls, v: int) -> int:
        return max(0, v)

    def team_summary(self) -> str:
        backend = (
            "None (client-only / static app)"
            if self.backend_developers == 0
            else str(self.backend_developers)
        )
        return f"{backend} backend, {self.frontend_developers} frontend"
