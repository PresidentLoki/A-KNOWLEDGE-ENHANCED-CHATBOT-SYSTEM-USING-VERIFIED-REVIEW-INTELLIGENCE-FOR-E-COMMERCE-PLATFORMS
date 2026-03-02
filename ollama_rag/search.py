import ollama, chromadb
from utilities import getconfig

embedmodel = getconfig()["embedmodel"]
mainmodel = getconfig()["mainmodel"]
chroma = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma.get_or_create_collection("buildragwithpython")

query = input("input: ")
queryembed = ollama.embeddings(model=embedmodel, prompt=query)['embedding']

relevantdocs = collection.query(query_embeddings=[queryembed], n_results=5)["documents"][0]
docs = "\n\n".join(relevantdocs)

modelquery = f"""
You are a cybersecurity assistant. Based only on the following context, carefully read and analyze each part 
of the context before determining which *single* type of cyber attack the user might be facing based on their query.

Context:
{docs}

---

Given the above context, what type of cyber attack may have occurred based on the problem described in the query: '{query}'? At the end, i want to know the attack from the context based on my query

Important instructions:
1. Carefully read and analyze *all parts* of the context to ensure you fully understand the situation before making a decision.
2. Focus on identifying *one primary attack type* based on the context and query.
3. Only mention multiple attacks if the context *clearly shows evidence* of more than one attack. Otherwise, *focus solely on one attack*.
4. If the query or context is *not related to cybersecurity*, respond with: "The query is not related to a cybersecurity issue, and I cannot provide an answer."

After identifying the attack:
1. Provide a brief description of the attack and explain how it typically operates.
2. Describe the potential effects or impact this attack has on the victim.
3. Finally, suggest practical solutions or mitigation steps to resolve or prevent the attack.
"""


print("\n",modelquery)
stream = ollama.generate(model=mainmodel, prompt=modelquery, stream=True)

for chunk in stream:
  if chunk["response"]:
    print(chunk['response'], end='', flush=True)
