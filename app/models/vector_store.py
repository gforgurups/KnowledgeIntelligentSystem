from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    def __init__(self, path):
        self.embeddings = OpenAIEmbeddings()
        self.vectore_store = Chroma(
            persist_directory = path,
            embedding_function = self.embeddings
        )
        self.path = path

    
    def add_documents(self, documents):
        self.vectore_store.add_documents(documents)
    

    def similarity_search(self, query, k=4):
        return self.vectore_store.similarity_search(query, k=k)
