from langchain_core.tools import tool
from ... import get_vector_store


@tool
def retrieval_tool(user_query: str) -> int:
    """
    Takes user_query (string) and fetches context from the vector_store to answer the user_query .

    Args:
        user_query (str) : first integer value

    Returns:
        context (str) : returns a string value that is the retrieved context with respect to the user_query
    """

    vector_store = get_vector_store()
    docs = vector_store.similarity_search(user_query, k=5)
    context = ""
    for doc in docs:
        context += doc.page_content

    return f"## User Query : {user_query}\n## Retrieved Context : {context}"