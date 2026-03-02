import ollama
import time
import chromadb
import re

embedmodel = 'nomic-embed-text'
mainmodel = 'reviewphi3'
#mainmodel = 'dsr1'
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

# Function to create a model prompt
def create_prompt(reviews: str, user_query: str) -> str:
    return f"""
Reviews:
{reviews}

User Query: {user_query}
"""

# Function to generate a response using the Ollama model
def generate_response(prompt: str) -> str:
    try:
        stream = ollama.generate(model=mainmodel, prompt=prompt, stream=True)
        response = ""
        for chunk in stream:
            if chunk["response"]:
                response += chunk["response"]
        return response.strip()
    except Exception as e:
        raise RuntimeError(f"An error occurred while generating a response: {e}")

# Main function
def main():
    amazon_url = input("Enter the Amazon product URL: ")
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

            flag = True

            while flag:
                user_query = input("\nEnter your query(type 'bye' to exit): ")
                if user_query!='bye':
                    try:
                        
                        # Create a prompt for the model
                        prompt = create_prompt(docs, user_query)
                        # Generate a response using the Ollama model
                        
                        start_time = time.time()
                        response = generate_response(prompt)

                        # Display the chatbot response
                        print("\nChatbot Response:")
                        print(response)

                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        print(f"\nResponse time: {elapsed_time:.2f} seconds\n")

                    except ValueError as e:
                        print(e)
                    except RuntimeError as e:
                        print(e)
                else:
                    flag=False

    except ValueError as e:
        print(e)  # Handle invalid Amazon URL
    

if __name__ == "__main__":
    main()
