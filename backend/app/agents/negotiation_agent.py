from app.llm.factory import get_groq_chat
from app.llm.structured import invoke_structured
from app.models.planning import PlanningEstimate
from app.models.project import Project
from app.prompts.templates import NEGOTIATION_PROMPT
from app.tools.project_tools import get_negotiation_tools, set_project_context

# 1- system prompt
# 2- human prompt (context)
# 3- query (input)
def _history_messages(project: Project) -> list:
    from langchain_core.messages import AIMessage, HumanMessage

    msgs = []
    for m in project.chat_history[-20:]:
        if m.role == "user":
            msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            msgs.append(AIMessage(content=m.content))
    return msgs


def run_negotiation_agent(project: Project, user_message: str) -> str:
    set_project_context(project.id)
    llm = get_groq_chat()
    tools = get_negotiation_tools()

    # binding
    llm_with_tools = llm.bind_tools(tools)

    # chain
    estimate = project.negotiated_estimate or project.estimate
    estimate_json = estimate.model_dump_json() if estimate else "{}"

    chain = NEGOTIATION_PROMPT | llm_with_tools
    response = chain.invoke({
        "history": _history_messages(project),
        "input": user_message,
        "estimate_json": estimate_json,
    })

#{
#    "name": "accept_proposal",
#    "args": {
#        "notes": "I agree with the estimate."
#    }
#}
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
            args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
            if name == "accept_proposal":
                notes = args.get("notes", "") if isinstance(args, dict) else ""
                tools[0].invoke({"notes": notes})
                return "Great! Proposal accepted. We will now generate your SRS document."

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content


def adjust_estimate(project: Project, user_message: str) -> PlanningEstimate:
    # 1- system prompt
    # 2- human prompt (context)
    # 3- query (input)
    llm = get_groq_chat()
    base = project.negotiated_estimate or project.estimate
    if not base:
        return project.estimate 
    return invoke_structured(
        llm,
        PlanningEstimate,
        "Return an updated project estimate reflecting customer feedback.",
        "Current estimate:\n{estimate}\n\nCustomer feedback:\n{feedback}",
        {
            "estimate": base.model_dump_json(indent=2),
            "feedback": user_message,
        },
    )