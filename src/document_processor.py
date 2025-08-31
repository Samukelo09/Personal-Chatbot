import os
import re
from typing import List, Dict, Any
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class DocumentProcessor:
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.embeddings = OpenAIEmbeddings()
        
    def load_documents(self):
        documents = []

        for filename in os.listdir(self.data_directory):
            file_path = os.path.join(self.data_directory, filename)
            
            try:
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)

                elif filename.endswith(".txt") or filename.endswith(".md"):
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs = loader.load()
                    documents.extend(docs)

            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                continue

        return documents
    
    def process_documents(self):
        print("Loading documents...")
        documents = self.load_documents()

        print(f"Loaded {len(documents)} documents.")

        print("Splitting documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks.")

        print("Creating vector store...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )

        vector_store.persist()
        print("Vector store created and persisted.")

        return vector_store
