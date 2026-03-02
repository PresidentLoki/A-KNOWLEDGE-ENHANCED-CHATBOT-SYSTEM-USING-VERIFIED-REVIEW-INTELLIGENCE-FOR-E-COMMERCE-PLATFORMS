import os
import json
import ollama, chromadb, time
# from utilities import getconfig
from mattsollamatools import chunker, chunk_text_by_sentences  

collectionname = "buildragwithpython"

chroma = chromadb.PersistentClient(path="./chromadb")
print(chroma.list_collections())

if any(collection.name == collectionname for collection in chroma.list_collections()):
    print('Deleting existing collection')
    chroma.delete_collection(collectionname)

collection = chroma.get_or_create_collection(name=collectionname, metadata={"hnsw:space": "cosine"})
# embedmodel = getconfig()["embedmodel"]
embedmodel='nomic-embed-text'

json_folder = "sources"  

starttime = time.time()

for filename in os.listdir(json_folder):
    if filename.endswith(".json"):  
        json_path = os.path.join(json_folder, filename)
        
        # Open and read the JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Check if data is a list (as the error suggests it is)
        if isinstance(data, list):
            # If it's a list, iterate over it or select the first item
            for item in data:
                full_text = item.get('reviews', '')  # Adjust this key to match the structure
                product_id = item.get('asin', '')  # Adjust this key to match the structure
                
                # If full_text is a list, join it into a single string
                if isinstance(full_text, list):
                    full_text = " ".join(full_text)
                
                # Chunk the text by sentences
                chunks = chunk_text_by_sentences(source_text=full_text, sentences_per_chunk=7, overlap=0)
                print(f"Processing {filename} with {len(chunks)} chunks")
                
                for index, chunk in enumerate(chunks):
                    embed = ollama.embeddings(model=embedmodel, prompt=chunk)['embedding']
                    print(".", end="", flush=True)
                    collection.add([filename + str(index)], [embed], documents=[chunk], metadatas={"source": filename, "product_id": product_id})
        else:
            print(f"Skipping {filename} as it does not have a list format")

print("--- %s seconds ---" % (time.time() - starttime))
