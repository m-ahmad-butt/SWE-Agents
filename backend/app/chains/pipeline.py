from app.agents.backend_engineer import run_backend_engineer
from app.agents.documentation_agent import run_documentation_agent
from app.agents.frontend_engineer import run_frontend_engineer
from app.agents.negotiation_agent import adjust_estimate
from app.agents.planning_analyst import run_planning_analyst
from app.agents.project_manager import run_project_manager
from app.agents.requirement_engineer import extract_requirements
from app.agents.srs_generator import run_srs_generator
from app.codegen.writer import list_project_files
from app.export.pdf import safe_export_srs_pdf, save_srs_markdown
from app.export.run_guide import save_run_guide
from app.models.project import MilestoneStatus, Project, ProjectPhase
from app.rag.store import index_text
from app.storage.json_store import load_project, save_project


#_set_phase(
#    project,
#    ProjectPhase.MILESTONE_CODING,
#    "backend_engineer",
#    "Backend Engineer is working..."
#)
def _set_phase(project: Project, phase: ProjectPhase, agent: str, msg: str) -> Project:
    project.phase = phase
    project.active_agent = agent
    project.status_message = msg
    return save_project(project)

# req + plan + negotiation agent then they will save project to json file
def run_planning_phase(project_id: str) -> Project:
    project = load_project(project_id)
    project = _set_phase(
        project, ProjectPhase.PLANNING, "planning_analyst", "Planning Analyst is estimating..."
    )
    if not project.requirements:
        project.requirements = extract_requirements(project)
    project.estimate = run_planning_analyst(project.requirements)
    project.negotiated_estimate = project.estimate
    project = _set_phase(
        project,
        ProjectPhase.NEGOTIATION,
        "negotiation_agent",
        f"Estimate ready: ${project.estimate.estimated_cost_usd}, "
        f"{project.estimate.timeline_months} months. Negotiation Agent is ready.",
    )
    est = project.estimate
    project.add_message(
        "assistant",
        f"Planning complete!\n\n"
        f"- Timeline: {est.timeline_months} months\n"
        f"- Cost: ${est.estimated_cost_usd:,}\n"
        f"- Complexity: {est.complexity}\n"
        f"- Team: {est.team_summary()}\n\n"
        "Negotiation Agent: What is your budget? Any changes you'd like?",
        agent="planning_analyst",
    )
    return save_project(project)

# srs generation phase
def run_srs_phase(project_id: str) -> Project:
    project = load_project(project_id)
    project = _set_phase(
        project, ProjectPhase.SRS_GENERATION, "srs_generator", "SRS Generator is working..."
    )
    req = project.requirements
    est = project.negotiated_estimate or project.estimate
    if not req or not est:
        raise ValueError("Missing requirements or estimate")
    project.srs = run_srs_generator(req, est)
    project.srs_markdown = project.srs.to_markdown()
    save_srs_markdown(project)
    index_text(project.id, project.srs_markdown, metadata={"type": "srs"})
    project.add_message(
        "assistant",
        "SRS document generated successfully.",
        agent="srs_generator",
    )
    return save_project(project)


# proj manager phase
def run_milestone_planning(project_id: str) -> Project:
    project = load_project(project_id)
    project = _set_phase(
        project,
        ProjectPhase.MILESTONE_PLANNING,
        "project_manager",
        "Project Manager is splitting milestones...",
    )
    if not project.srs:
        raise ValueError("SRS missing")
    project.milestones = run_project_manager(project.srs)
    project.current_milestone_index = 0
    titles = ", ".join(m.title for m in project.milestones)
    project.add_message(
        "assistant",
        f"Project split into {len(project.milestones)} milestones: {titles}",
        agent="project_manager",
    )
    return save_project(project)

# backend engineer phase
def start_milestone_coding(project_id: str) -> Project:
    """Prepare milestone coding — backend engineer first; actual work runs via advance."""
    project = load_project(project_id)
    milestone = project.current_milestone()
    if not milestone:
        project.phase = ProjectPhase.COMPLETED
        return save_project(project)

    milestone.status = MilestoneStatus.IN_PROGRESS
    project.last_backend_summary = ""
    project.last_frontend_summary = ""
    return _set_phase(
        project,
        ProjectPhase.MILESTONE_CODING,
        "backend_engineer",
        f"Backend Engineer working on Milestone {milestone.number}: {milestone.title}...",
    )

# frontend engineer phase + documentation agent phase
def advance_milestone_work(project_id: str) -> Project:
    """Run one milestone step: backend → frontend → documentation → customer review."""
    project = load_project(project_id)
    milestone = project.current_milestone()
    if not milestone:
        return project

    if project.phase == ProjectPhase.MILESTONE_CODING:
        if project.active_agent == "backend_engineer":
            backend_summary = run_backend_engineer(project, milestone)
            project = load_project(project_id)
            project.last_backend_summary = backend_summary
            project.generated_files = list_project_files(project.id)
            return _set_phase(
                project,
                ProjectPhase.MILESTONE_CODING,
                "frontend_engineer",
                f"Frontend Engineer working on Milestone {milestone.number}: {milestone.title}...",
            )

        if project.active_agent == "frontend_engineer":
            frontend_summary = run_frontend_engineer(project, milestone)
            project = load_project(project_id)
            project.last_frontend_summary = frontend_summary
            project.generated_files = list_project_files(project.id)
            return _set_phase(
                project,
                ProjectPhase.MILESTONE_DOCUMENTATION,
                "documentation_agent",
                "Documentation Agent is writing milestone docs...",
            )

    if project.phase == ProjectPhase.MILESTONE_DOCUMENTATION:
        run_documentation_agent(
            project,
            milestone,
            project.last_backend_summary,
            project.last_frontend_summary,
        )
        milestone.status = MilestoneStatus.PENDING_REVIEW
        save_project(project)
        safe_export_srs_pdf(project)

        backend_summary = project.last_backend_summary
        frontend_summary = project.last_frontend_summary
        project = _set_phase(
            project,
            ProjectPhase.MILESTONE_REVIEW,
            "customer_review",
            f"Milestone {milestone.number} ready for your review. Approve or request changes.",
        )
        project.add_message(
            "assistant",
            f"Milestone {milestone.number} ({milestone.title}) is complete.\n"
            f"Backend: {backend_summary}\nFrontend: {frontend_summary}\n\n"
            "Please review the code and documentation. Reply 'approve' or describe changes.",
            agent="documentation_agent",
        )
        return save_project(project)

    return project

# complete project phase
def complete_project(project_id: str) -> Project:
    """Finalize project: generate README, export docs, notify user."""
    project = load_project(project_id)
    project.run_guide_markdown = save_run_guide(project)
    project.generated_files = list_project_files(project.id)
    safe_export_srs_pdf(project)

    project.phase = ProjectPhase.COMPLETED
    project.active_agent = "customer_review"
    project.status_message = "Project complete! Download the ZIP and follow README.md to run."
    project.add_message(
        "assistant",
        "All milestones approved. **Project complete!**\n\n"
        "**Next steps:**\n"
        "1. Click **ZIP** (top-right) to download your generated application\n"
        "2. Unzip the archive on your machine\n"
        "3. Open **README.md** inside the folder and follow the setup instructions\n"
        "4. Start the backend, then the frontend, and open the app in your browser\n\n"
        "You can also download the **PDF** for full SRS and milestone documentation, "
        "or view the run guide under **Files & Docs → Run Guide**.",
        agent="project_manager",
    )
    return save_project(project)

# approve milestone phase
def approve_milestone(project_id: str, milestone_number: int) -> Project:
    project = load_project(project_id)
    idx = project.current_milestone_index
    if idx >= len(project.milestones):
        return project
    ms = project.milestones[idx]
    if ms.number != milestone_number:
        raise ValueError("Milestone number mismatch")

    ms.status = MilestoneStatus.APPROVED
    ms.revision_feedback = ""
    save_project(project)
    safe_export_srs_pdf(project)

    next_idx = idx + 1
    if next_idx >= len(project.milestones):
        return complete_project(project_id)

    project = load_project(project_id)
    project.current_milestone_index = next_idx
    project.milestones[next_idx].status = MilestoneStatus.IN_PROGRESS
    project.add_message(
        "assistant",
        f"Milestone {ms.number} approved. Starting Milestone {project.milestones[next_idx].number}...",
        agent="project_manager",
    )
    save_project(project)
    return start_milestone_coding(project_id)

# reject milestone phase
def reject_milestone(project_id: str, milestone_number: int, feedback: str) -> Project:
    project = load_project(project_id)
    idx = project.current_milestone_index
    ms = project.milestones[idx]
    ms.status = MilestoneStatus.REVISION
    ms.revision_feedback = feedback
    project.add_message("assistant", f"Revision requested: {feedback}", agent="customer_review")
    save_project(project)
    return start_milestone_coding(project_id)

# run proposal to srs phase
def run_proposal_to_srs(project_id: str) -> Project:
    """SRS → milestone planning → start first milestone (coding runs step-by-step via advance)."""
    project = run_srs_phase(project_id)
    project = run_milestone_planning(project.id)
    return start_milestone_coding(project.id)

# advance project phase
def advance_project(project_id: str) -> Project:
    project = load_project(project_id)
    phase = project.phase

    if phase == ProjectPhase.REQUIREMENTS and project.requirements_complete:
        return run_planning_phase(project_id)
    if phase == ProjectPhase.PLANNING:
        return run_planning_phase(project_id)
    if phase == ProjectPhase.NEGOTIATION and project.proposal_accepted:
        return run_proposal_to_srs(project_id)
    if phase == ProjectPhase.SRS_GENERATION:
        return run_srs_phase(project_id)
    if phase == ProjectPhase.MILESTONE_PLANNING:
        return run_milestone_planning(project_id)
    if phase in (ProjectPhase.MILESTONE_CODING, ProjectPhase.MILESTONE_DOCUMENTATION):
        return advance_milestone_work(project_id)

    return project
