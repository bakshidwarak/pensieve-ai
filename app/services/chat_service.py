from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as LCOpenAI
from app.embeddings_store import vector_store

llm = LCOpenAI(temperature=0.0, model_name="gpt-4o-mini")

async def answer_query(query: str, top_k: int = 4, tag_filters: list | None = None):
    retriever = vector_store.store.as_retriever(search_kwargs={"k": top_k})
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    answer = qa.run(query)
    docs = retriever.get_relevant_documents(query) if hasattr(retriever, "get_relevant_documents") else []
    sources = [d.metadata.get("id") or d.metadata.get("source") for d in docs][:top_k]
    return {"answer": answer, "sources": sources}
