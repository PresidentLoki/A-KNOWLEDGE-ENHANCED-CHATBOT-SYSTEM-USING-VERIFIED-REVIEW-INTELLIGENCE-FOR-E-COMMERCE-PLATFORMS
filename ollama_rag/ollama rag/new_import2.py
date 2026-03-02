import os
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

txt_folder = "sources"  

starttime = time.time()

for filename in os.listdir(txt_folder):
    if filename.endswith(".txt"):  
        txt_path = os.path.join(txt_folder, filename)
        
        # Open and read the text file
        with open(txt_path, 'r', encoding='utf-8') as file:
            full_text = file.read()
        
        # Chunk the text by sentences
        chunks = chunk_text_by_sentences(source_text=full_text, sentences_per_chunk=7, overlap=0)
        print(f"Processing {filename} with {len(chunks)} chunks")
        
        for index, chunk in enumerate(chunks):
            # Generate embeddings for each chunk
            embed = ollama.embeddings(model=embedmodel, prompt=chunk)['embedding']
            print(".", end="", flush=True)
            # Add each chunk to the collection
            collection.add([filename + str(index)], [embed], documents=[chunk], metadatas={"source": filename})

print("--- %s seconds ---" % (time.time() - starttime))
