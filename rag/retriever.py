from typing import List, Dict

"""
    retrieve top-k most similar chunks from the FAISS index for a given query.
    args:
        vs: FAISS vector store
        query: user question
        k: number of chunks to return (default 6)
    returns:
        context: concatenated string of retrieved content
        docs: list of retrieved Document objects
    """
def retrieve(vs, query: str, k: int = 6):

    # run similarity search
    docs = vs.similarity_search(query, k=k)

    # join results into a single string for LLM input
    context = "\n\n".join(
        [f"[Doc {i+1}]: {doc.page_content}" for i, doc in enumerate(docs)]
    )
    return context, docs
