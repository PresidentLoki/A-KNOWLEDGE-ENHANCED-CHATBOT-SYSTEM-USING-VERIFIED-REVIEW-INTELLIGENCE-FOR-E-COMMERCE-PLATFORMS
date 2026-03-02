import ollama, chromadb
# from utilities import getconfig

# embedmodel = getconfig()["embedmodel"]
embedmodel='nomic-embed-text'
# mainmodel = getconfig()["mainmodel"]
mainmodel='llama3'
chroma = chromadb.PersistentClient(path="./chromadb")
collection = chroma.get_or_create_collection("buildragwithpython")

query = input("input: ")
queryembed = ollama.embeddings(model=embedmodel, prompt=query)['embedding']

relevantdocs = collection.query(query_embeddings=[queryembed], n_results=5)["documents"][0]
docs = "\n\n".join(relevantdocs)

modelquery = f"""
You are a personal e-shopping assistant. Your task is to analyze product reviews provided in the context to answer user queries
about the product's quality, durability, features, and other relevant aspects.


Context:
{docs}

Query: {query}
---

Task:

1. Analyze the reviews: Carefully read and understand the product reviews provided in the context.
2. Identify relevant information: Extract specific information related to the user's query, such as quality, durability, features, performance, or customer satisfaction.
3. Formulate a comprehensive response: Provide a clear and concise answer to the user's query, incorporating insights from the reviews.
4. Highlight key points: Emphasize the most important aspects of the product based on the reviews, such as its strengths, weaknesses, or unique features.
5. Provide recommendations: If appropriate, offer suggestions or recommendations to the user, such as alternative products or specific features to consider.
"""


print("\n",modelquery)
stream = ollama.generate(model=mainmodel, prompt=modelquery, stream=True)

for chunk in stream:
  if chunk["response"]:
    print(chunk['response'], end='', flush=True)
