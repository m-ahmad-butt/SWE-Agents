from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# text structure base text splitter
def split_text(text: str, metadata: dict | None = None) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=100
        )
    docs = splitter.create_documents(
        [text], 
        metadatas=[metadata or {}]
        )
    return docs
