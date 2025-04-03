from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyMuPDFLoader

from ..agent import embeddings
from .. import update_vector_store

def process_pdf(file_path: str) -> str:
    """Extracts pages from a given PDF file and into vectore store"""

    loader = PyMuPDFLoader(file_path)
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    if not pages:
        return "I couldn't extract text from this PDF. Please try another document."
    
    vector_store = InMemoryVectorStore.from_documents(pages, embeddings)
    update_vector_store(vector_store)
    
    return "I have read the pdf documents uploaded, do you have any questions with reference to the document for me?"
