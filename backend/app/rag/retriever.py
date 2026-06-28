from langchain_core.documents import Document

from app.rag.store import get_vectorstore

# Vector Store -> MMR retriever
def get_mmr_retriever(project_id: str, k: int = 4, fetch_k: int = 10):
    store = get_vectorstore(project_id)
    return store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k},
    )

# MMR retrieval
def retrieve_context(project_id: str, query: str, k: int = 4) -> str:
    try:
        retriever = get_mmr_retriever(project_id, k=k)
        docs: list[Document] = retriever.invoke(query)
        if not docs:
            return ""
        return "\n\n---\n\n".join(d.page_content for d in docs)
    except Exception:
        return ""
