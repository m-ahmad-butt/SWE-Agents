from langchain_core.messages import AIMessage, HumanMessage
from app.llm.factory import get_groq_chat
from app.llm.structured import invoke_structured
from app.models.project import Project
from app.models.requirements import RequirementsSummary
from app.prompts.templates import REQUIREMENT_ENGINEER_PROMPT
from app.tools.project_tools import get_requirement_tools, set_project_context


def _history_messages(project: Project) -> list:
    msgs = []
    for m in project.chat_history[-20:]:
        if m.role == "user":
            msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            msgs.append(AIMessage(content=m.content))
    return msgs


def run_requirement_engineer(project: Project, user_message: str) -> str:
    set_project_context(project.id)
    llm = get_groq_chat()
    tools = get_requirement_tools()

    # binding
    llm_with_tools = llm.bind_tools(tools)

    # chain
    chain = REQUIREMENT_ENGINEER_PROMPT | llm_with_tools

    # invoke with inputs
    response = chain.invoke({
        "history": _history_messages(project),
        "input": user_message,
    })

    # AIMessage(
    #     content="",
    #     tool_calls=[
    #         {
    #             "name": "mark_requirements_complete",
    #             "args": {
    #                 "summary": "Gym Management System with authentication..."
    #             }
    #         }
    #     ]
    # )

    # Handle tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
            args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
            if name == "mark_requirements_complete":
                summary = args.get("summary", user_message) if isinstance(args, dict) else user_message

                # calling that tool with parameters
                tools[0].invoke({"summary": summary})
                return (
                    "Thank you! I have collected all requirements. "
                    "Passing them to the Planning Analyst now."
                )

    # return the content of the response
    content = response.content if isinstance(response.content, str) else str(response.content)
    return content




# output parser calling
def extract_requirements(project: Project) -> RequirementsSummary:
    llm = get_groq_chat()

    #[
    #    Message(role="user", content="I want a Gym Management System"),
    #    Message(role="assistant", content="Who are the users?"),
    #    Message(role="user", content="Admin, Trainer, Member")
    #]

    # conversation -> list of messages

    # 1- system prompt
    # 2- human prompt (context)
    # 3- query (input)
    conversation = "\n".join(
        f"{m.role}: {m.content}" for m in project.chat_history
    )
    result = invoke_structured(
        llm,
        RequirementsSummary,
        "Extract structured requirements from the conversation.",
        "Conversation:\n{conversation}",
        {"conversation": conversation},
    )
    result.raw_conversation = conversation
    return result