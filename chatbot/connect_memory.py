from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import requests

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
API_MARKET = os.getenv("API_MARKET")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
DB_FAISS_PATH = "../vectorstore/db_faiss"
SARVAM_URL = "https://api.magicapi.dev/api/v1/sarvam/ai-models/translate"

def translate_text(text, source_lang, target_lang):
    headers = {
        'x-magicapi-key': API_MARKET,
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": target_lang,
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": False
    }
    try:
        response = requests.post(SARVAM_URL, headers=headers, json=data)
        return response.json().get("result", text)
    except Exception as e:
        return f"[Translation Error] {str(e)}"

def load_llm():
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    return ChatNVIDIA(
        model="mistralai/mistral-7b-instruct-v0.3",
        api_key=NVIDIA_API_KEY,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )

def get_lawgic_prompt():
    return '''
You are LawgicAI, a legal information assistant. Only answer questions strictly related to the legal context provided.
- If the user's question is not clearly about a legal matter, politely reply: "I can only help with legal questions. Please ask a question related to law or legal information."
- If you do not find the answer in the context, reply: "Please contact a legal official for such information."
- Do NOT make up information or try to answer irrelevant or personal opinion-based questions.
Use the pieces of information provided in context to answer the user's legal question clearly and simply.
Context: {context}
Question: {question}
'''

def custom_prompt(template=None):
    if template is None:
        template = get_lawgic_prompt()
    return PromptTemplate(template=template, input_variables=["context", "question"])

def main():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    llm = load_llm()
    template = get_lawgic_prompt()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True,
        chain_type_kwargs={'prompt': custom_prompt(template)}
    )
    user_query = input("Write your query here: ")
    response = qa_chain.invoke({'query': user_query})
    print("Result:", response["result"])
    print("Source documents:", response["source_documents"])
    # Optionally translate
    result = response["result"]
    translated = translate_text(result, "en-IN", "hi-IN")
    print("Hindi Translation:", translated)

if __name__ == "__main__":
    main()
