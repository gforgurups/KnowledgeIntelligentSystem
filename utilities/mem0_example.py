import os
from dotenv import load_dotenv
from mem0 import Memory 


#Configuration	  Class Used	                       Data Location	        API Key Required?
#Managed Cloud	  from mem0 import MemoryClient	Mem0   Managed Servers	        Yes (MEM0_API_KEY)
#Local Storage	  from mem0 import Memory	           Your Local Machine	    No (Except for your LLM provider)


#What It Does
#Persistent Context: Instead of forcing you to re-feed an entire chat transcript into an LLM on every turn, 
      #Mem0 dynamically extracts, updates, and stores durable facts, user preferences, and relationship structures.
#• Multi-Level Memory: It organizes context across different scopes, including User, Session, Agent, and Procedural memories.
#• Hybrid Retrieval: It uses a mix of semantic search, keyword scoring (BM25), and entity boosting to pull only relevant memories before an LLM call.

# SSL FIX
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

#Load environment variables dynamically based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH)

def run_observability_demo():
    #Configuration
    config={
        "vector_store":{
            "provider": "chroma",
            "config":{"collection_name":"rag_demo", "path":"db"}
        },
        "llm":{
            "provider":"openai",
            "config":{"model":"gpt-4o-mini", "temperature":0}
        }
    }

    #Initialize Memory
    memory = Memory.from_config(config)
    user_id="guru_123"

    messages = [
                    { "role": "user", "content": "Hi, I'm Guru. I'm a vegetarian and I'm allergic to nuts." },
                    { "role": "assistant", "content": "Hello Guru! I see that you're a vegetarian with a nut allergy." }
                ]

    memory.add(messages, user_id=user_id)

    query = "What can I cook for dinner tonight?"
    response = memory.search(query, filters={"user_id": user_id})
    memories = response.get('results') if isinstance(response, dict) else response
    print(memories)
    if memories:
        for res in memories:
            val = res.get('memory') or res.get('payload',{}).get('value')
            print(f"Observed Memory: {val} (Score: {res.get('score')})")

if __name__ == "__main__":
    run_observability_demo()