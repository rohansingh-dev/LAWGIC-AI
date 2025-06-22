from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os

load_dotenv()

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

def load_pdf_files(data):
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

documents = load_pdf_files(DATA_PATH)
print("length of documents: ", len(documents))

def create_chunks(extracted_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = splitter.split_documents(extracted_data)
    return chunks

chunks = create_chunks(documents)
print("length of chunks: ", len(chunks))

def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model

embedding_model = get_embedding_model()

DB_FAISS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vectorstore/db_faiss'))
db = FAISS.from_documents(chunks, embedding_model)
db.save_local(DB_FAISS_PATH)
