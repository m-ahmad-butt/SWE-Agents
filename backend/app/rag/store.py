from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from app.config import CHROMA_DIR
from app.rag.loader import split_text

# FakeEmbeddings for local Chroma indexing
def get_embeddings() -> Embeddings:
    return FakeEmbeddings(size=384)

# Chroma vector store
def get_vectorstore(project_id: str) -> Chroma:
    persist = str(CHROMA_DIR / project_id)
    return Chroma(
        collection_name=f"project_{project_id}",
        embedding_function=get_embeddings(),
        persist_directory=persist,
    )

# add documents into vector store
def index_documents(project_id: str, documents: list[Document]) -> None:
    if not documents:
        return
    store = get_vectorstore(project_id)
    store.add_documents(documents)

# add text into vector store
def index_text(project_id: str, text: str, metadata: dict | None = None) -> None:
    docs = split_text(text, metadata)
    index_documents(project_id, docs)
