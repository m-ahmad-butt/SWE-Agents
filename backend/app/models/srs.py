from pydantic import BaseModel, Field

# pydantic (output parser)
class SRSDocument(BaseModel):
    project_overview: str
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    actors: list[str]
    modules: list[str]
    user_flow: str
    technology_stack: list[str]
    acceptance_criteria: list[str]
    milestones_overview: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            "# Software Requirements Specification",
            "",
            "## Project Overview",
            self.project_overview,
            "",
            "## Functional Requirements",
        ]
        lines.extend(f"- {r}" for r in self.functional_requirements)
        lines.extend(["", "## Non-Functional Requirements"])
        lines.extend(f"- {r}" for r in self.non_functional_requirements)
        lines.extend(["", "## Actors"])
        lines.extend(f"- {a}" for a in self.actors)
        lines.extend(["", "## Modules"])
        lines.extend(f"- {m}" for m in self.modules)
        lines.extend(["", "## User Flow", self.user_flow, "", "## Technology Stack"])
        lines.extend(f"- {t}" for t in self.technology_stack)
        lines.extend(["", "## Acceptance Criteria"])
        lines.extend(f"- {c}" for c in self.acceptance_criteria)
        if self.milestones_overview:
            lines.extend(["", "## Milestones Overview"])
            lines.extend(f"- {m}" for m in self.milestones_overview)
        return "\n".join(lines)
