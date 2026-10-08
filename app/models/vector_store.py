import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings


class VectorStore:
    def __init__(self, persist_directory: str = "db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()

        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        self.vectorstore.add_documents(documents)

    def similarity_search(self, query: str, k: int = 3):
        return self.vectorstore.similarity_search(query, k=k)
