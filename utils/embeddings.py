import os
import streamlit as st
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

## INSTALL ##
# data folder : where documents are uploaded 
DATA_PATH = "data"

# chroma folder : where vector database is stored  
CHROMA_PATH = "chroma"

# gguf models
MODEL_PATH = "models"


def install():
    createpath(DATA_PATH)
    if createpath(CHROMA_PATH):
        import chromadb
        client = chromadb.PersistentClient(CHROMA_PATH)
    
def createpath(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else :
        return False


@st.cache_resource
def EMBEDDINGS():
    APP_EMBEDDINGS = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # APP_EMBEDDINGS = embedding_functions.DefaultEmbeddingFunction()
    # APP_EMBEDDINGS = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return APP_EMBEDDINGS






