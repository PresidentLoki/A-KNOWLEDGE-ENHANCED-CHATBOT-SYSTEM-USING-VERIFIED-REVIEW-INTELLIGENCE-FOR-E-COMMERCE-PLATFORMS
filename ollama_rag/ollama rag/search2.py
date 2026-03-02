import ollama
import chromadb
import re

# embedmodel = getconfig()["embedmodel"]
embedmodel = 'nomic-embed-text'
# mainmodel = getconfig()["mainmodel"]
mainmodel = 'llama3'
chroma = chromadb.PersistentClient(path="./chromadb")
collection = chroma.get_or_create_collection("buildragwithpython")

# Function to extract ASIN from Amazon product link
def extract_asin_from_url(url: str) -> str:
    asin_pattern = r"\/dp\/([A-Z0-9]{10})"
    match = re.search(asin_pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Amazon product URL")

# Get the Amazon product link and user query as input
amazon_url = input("Enter the Amazon product URL: ")
query = input("Enter your query: ")

try:
    # Extract ASIN from the Amazon URL
    asin = extract_asin_from_url(amazon_url)
    print(f"Extracted ASIN: {asin}")

    # Check if the ASIN exists in the ChromaDB collection
    relevantdocs = collection.query(query_embeddings=[ollama.embeddings(model=embedmodel, prompt=asin)['embedding']], n_results=5)
    
    if not relevantdocs["documents"]:
        print(f"No reviews found for product with ASIN {asin}.")
    else:
        # Join relevant documents to form the context for the query
        docs = "\n\n".join(relevantdocs["documents"][0])

        # Prepare the prompt for the model
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

        # Print the model query for verification
        print("\n", modelquery)

        # Generate the response using the Ollama model
        stream = ollama.generate(model=mainmodel, prompt=modelquery, stream=True)

        # Print the response stream from Ollama
        for chunk in stream:
            if chunk["response"]:
                print(chunk['response'], end='', flush=True)

except ValueError as e:
    print(e)  # Handle invalid Amazon URL
