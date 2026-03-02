import os
import ollama, chromadb, time
from utilities import getconfig
from mattsollamatools import chunker, chunk_text_by_sentences
from langchain_community.document_loaders import PyPDFLoader  

collectionname = "buildragwithpython"

chroma = chromadb.HttpClient(host="localhost", port=8000)
print(chroma.list_collections())

if any(collection.name == collectionname for collection in chroma.list_collections()):
    print('Deleting existing collection')
    chroma.delete_collection(collectionname)

collection = chroma.get_or_create_collection(name=collectionname, metadata={"hnsw:space": "cosine"})
embedmodel = getconfig()["embedmodel"]

pdf_folder = "sources"  

starttime = time.time()

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):  
        pdf_path = os.path.join(pdf_folder, filename)
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()  
        
        full_text = " ".join([doc.page_content for doc in documents])
        
        chunks = chunk_text_by_sentences(source_text=full_text, sentences_per_chunk=7, overlap=0)
        print(f"Processing {filename} with {len(chunks)} chunks")
        
        for index, chunk in enumerate(chunks):
            embed = ollama.embeddings(model=embedmodel, prompt=chunk)['embedding']
            print(".", end="", flush=True)
            collection.add([filename + str(index)], [embed], documents=[chunk], metadatas={"source": filename})

print("--- %s seconds ---" % (time.time() - starttime))
