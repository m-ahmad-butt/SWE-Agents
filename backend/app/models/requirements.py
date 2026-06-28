from pydantic import BaseModel, Field

# pydantic (output parser)
class RequirementsSummary(BaseModel):
    project_name: str = Field(description="Short project name")
    project_type: str = Field(description="web, mobile, or desktop")
    description: str = Field(description="What the application does")
    key_features: list[str] = Field(description="Main features")
    target_users: list[str] = Field(description="Who will use the app")
    constraints: list[str] = Field(default_factory=list, description="Budget, timeline, tech constraints")
    raw_conversation: str = Field(default="", description="Full requirement conversation text")
