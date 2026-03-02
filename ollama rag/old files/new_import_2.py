from langchain.embeddings import OllamaEmbeddings
import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from tqdm import tqdm  
from utilities import getconfig

DATA_PATH = "sources"
CHROMA_PATH = "chroma"

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()  
    chunks = split_text(documents)
    print("Received chunks")
    save_to_chroma(chunks)

def load_documents():
    documents = []
    
    
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]

    
    for filename in tqdm(pdf_files, desc="Loading PDFs", unit="file"):
        file_path = os.path.join(DATA_PATH, filename)
        loader = PyPDFLoader(file_path)
        pdf_documents = loader.load()
        documents.extend(pdf_documents)  
    
    print(f"Loaded {len(documents)} documents from PDFs.")
    return documents

def split_text(documents: list):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    
    
    chunks = []
    for doc in tqdm(documents, desc="Splitting text", unit="document"):
        chunks.extend(text_splitter.split_documents([doc]))

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    
    
    document = chunks[10] if len(chunks) > 10 else chunks[0]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list):
    
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    model_kwargs = model_kwargs = {'device':'gpu', 'trust_remote_code': True}

    
    print("Saving chunks to Chroma...")
    
    embeddings_model = OllamaEmbeddings(model=getconfig()["embedmodel"],model_kwargs=model_kwargs)
    db = Chroma.from_documents(
        tqdm(chunks, desc="Embedding chunks", unit="chunk"),
        embeddings_model,
        persist_directory=CHROMA_PATH
    )
    
    print("Chroma from doc done")
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
