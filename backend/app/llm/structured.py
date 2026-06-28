from typing import TypeVar
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

# generic type
T = TypeVar("T", bound=BaseModel)

# output parser schema
# 1- system prompt
# 2- human prompt (context)
# 3- query (input)
def invoke_structured(
    llm: BaseChatModel,
    model_class: type[T],
    system: str,
    human: str,
    inputs: dict,
) -> T:
    """Parse LLM output as JSON into Pydantic (Groq-safe, no tool calling)."""
    parser = PydanticOutputParser(pydantic_object=model_class)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system + "\n\nRespond with valid JSON only.\n{format_instructions}"),
        ("human", human),
    ]).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    return chain.invoke(inputs)
