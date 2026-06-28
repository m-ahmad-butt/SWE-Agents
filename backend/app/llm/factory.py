from langchain_groq import ChatGroq
from app.config import (
    GROQ_API_KEY,
    GROQ_CHAT_MODEL,
    GROQ_CODE_MODEL,
    GROQ_DOC_MODEL,
    GROQ_STRUCTURED_MODEL,
)

# llm models (GROQ)
def get_groq_chat(temperature: float = 0.3) -> ChatGroq:
    return ChatGroq(
        model=GROQ_CHAT_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )


def get_groq_structured(temperature: float = 0.1) -> ChatGroq:
    return ChatGroq(
        model=GROQ_STRUCTURED_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )


def get_groq_code(temperature: float = 0.2) -> ChatGroq:
    return ChatGroq(
        model=GROQ_CODE_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )


def get_groq_doc(temperature: float = 0.2) -> ChatGroq:
    return ChatGroq(
        model=GROQ_DOC_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )
