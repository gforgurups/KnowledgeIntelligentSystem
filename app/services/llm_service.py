from langchain.chat_models import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from config import Config

class LLMService:
    def __init__(self,vector_store):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.7
        )
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})  
        
        self.session_store = {}
        # Setup History-Aware Retriever 
        # This rewrites the user's question into a standalone query using history
        self.contextualize_q_system_prompt = (

            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
                    ("system", self.contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ])

        # Create the history-aware retriever using LCEL primitives under the hood
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, self.contextualize_q_prompt
        )

        # Setup Document QA Chain
        # This takes retrieved context and answers the user's standalone question
        self.qa_system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know.\n\n"
            "{context}"
        )
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Create a chain that formats documents into the prompt
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)

        # Combine them into the Final Retrieval Chain
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)

        #  Wrap an existing RAG chain with RunnableWithMessageHistory
        self.conversational_rag_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self.get_session_history,
            input_messages_key="input",          # Maps the user query
            history_messages_key="chat_history", # Matches the placeholder in your prompt
            output_messages_key="answer"         # Tracks what the model responded with
        )


    def get_session_history(self,session_id: str):
        """Retrieves or creates a fresh chat history object for a given session."""
        if session_id not in self.session_store:
            self.session_store[session_id] = InMemoryChatMessageHistory()
        return self.session_store[session_id]

    def generate_response(self, query, session_id: str):
        try:
            config = {"configurable": {"session_id": session_id}}
            response = self.conversational_rag_chain.invoke(
                {"input": query},
                config=config
            )
            return response['answer']
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I couldn't process your request at the moment."          
      