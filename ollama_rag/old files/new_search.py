import ollama
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from utilities import getconfig

CHROMA_PATH = "chroma"

def main():
    perform_query()

def perform_query():
    # Load the Chroma vector store from the persisted directory
    print("Loading Chroma vector store from:", CHROMA_PATH)

    # Initialize embeddings model (Ollama)
    embeddings_model = OllamaEmbeddings(model=getconfig()["embedmodel"])

    # Load the existing Chroma DB
    chroma = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings_model)

    # Take input query from user
    query = input("Input your query: ")

    # Generate embeddings for the query using Ollama
    query_embed = ollama.embeddings(model=getconfig()["embedmodel"], prompt=query)['embedding']
    
    # Query the Chroma collection using the generated query embeddings
    print(f"Querying Chroma with '{query}'...")
    result = chroma.similarity_search_by_vector(query_embed, k=5)

    # Retrieve the most relevant documents
    relevant_docs = [doc.page_content for doc in result]
    
    # Print the retrieved documents
    print("\nMost relevant documents:")
    for i, doc in enumerate(relevant_docs):
        print(f"\nDocument {i+1}:\n{doc}")
    print(relevant_docs)
    # Combine the retrieved documents for further processing or model usage
    docs_context = "\n\n".join(relevant_docs)
    
    # Build a model query based on the retrieved context
    model_query = build_model_query(docs_context, query)

    # Generate the model response using Ollama
    print("\nGenerating model response...\n")
    generate_response(model_query)

def build_model_query(docs_context, query):
    model_query = f"""You are a cybersecurity assistant. Based only on the following context, determine which type of attack the user might be facing.

Context:
{docs_context}

---

Given the above context, what type of cyber attack may have occurred based on the problem described? Use the full context and decide. '{query}'"""
    
    return model_query

def generate_response(prompt):
    # Use the main model to generate the response (assuming it's an Ollama model)
    stream = ollama.generate(model=getconfig()["mainmodel"], prompt=prompt, stream=True)

    # Stream the response chunks from the Ollama model
    for chunk in stream:
        if chunk["response"]:
            print(chunk['response'], end='', flush=True)

if __name__ == "__main__":
    main()
