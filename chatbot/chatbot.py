import streamlit as st
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
DB_FAISS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vectorstore/db_faiss'))
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
        "enable_preprocessing": True
    }
    try:
        response = requests.post(SARVAM_URL, headers=headers, json=data)
        return response.json().get("result", text)
    except Exception as e:
        return f"[Translation Error] {str(e)}"

@st.cache_resource
def get_vectorstore():
    faiss_index = os.path.join(DB_FAISS_PATH, 'index.faiss')
    faiss_pkl = os.path.join(DB_FAISS_PATH, 'index.pkl')
    if not (os.path.exists(faiss_index) and os.path.exists(faiss_pkl)):
        st.error("Vectorstore is missing. Please run: python chatbot/create_memory.py")
        st.stop()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

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
    # Streamlit app title
    st.title("\U0001F4DA Lawgic AI Chatbot")
    
    # Language selection radio button
    language = st.radio("Choose your language:", options=["English", "Hindi"])
    
    # Initialize session state for messages if not already done
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    # Display chat messages from session state
    for msg in st.session_state.messages:
        st.chat_message(msg['role']).markdown(msg['content'])
        
    # User input for legal question
    user_input = st.chat_input("Ask your legal question here...")
    if user_input:
        original_input = user_input
        
        # Translate user input to English if the selected language is Hindi
        if language == "Hindi":
            user_input = translate_text(user_input, "hi-IN", "en-IN")
            
        # Display user message in the chat
        st.chat_message("user").markdown(original_input)
        
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": original_input})
        try:
            # Get vectorstore and language model
            vectorstore = get_vectorstore()
            llm = load_llm()
            
            # Define the prompt template for the legal assistant
            template = '''
You are LawgicAI, a professional assistant specializing in Indian law, answering strictly based on the project's provided legal documents and context. Your responses must always:

- Be strictly based on the provided legal context (Indian laws, acts, case studies, government documents, etc.) from this project.
- Be clear, concise, and professional:
    - Use bullet points for lists, steps, or key facts.
    - Use short paragraphs for explanations or context.
    - Combine both formats for clarity and readability.
- Use simple, direct language suitable for the general public.
- Avoid repetition, filler, speculation, or generic disclaimers unless absolutely necessary.
- Remain neutral, objective, and free from personal opinions.
- Reference relevant laws, sections, or context from the project when possible.
- Never make up information, speculate, or answer irrelevant/personal questions.
- Never engage in small talk or provide answers outside the project's legal scope.
- Do NOT repeat fallback or disclaimer messages unless the user's question is clearly out of scope.
- Always prioritize actionable, relevant, and project-specific information.

**Instructions:**
1. If the user's message is a greeting or small talk, reply only with:
    - "Hello! I can assist you with Indian legal matters from the project's context. Please ask your legal question."
    - Do not engage in further small talk or provide generic disclaimers.
2. If the user's message is not clearly about Indian law, legal rights, legal procedures, or legal topics relevant to the project, reply only with:
    - "I can only assist with questions related to Indian legal matters as covered in this project."
    - Do not provide any other information or generic disclaimers.
3. If the answer is not found in the provided context, reply only with:
    - "I could not find a specific answer in the project's Indian legal context."
    - "Please consult a qualified legal professional for further assistance."
4. For valid legal questions:
    - Start with a brief summary (1-2 sentences) if appropriate.
    - Follow with clear, well-organized bullet points for steps, requirements, or key facts.
    - Reference the context or law section from the project if possible.
    - Use simple, direct language.
    - Avoid unnecessary repetition, filler, or generic statements.
5. Never make up information, speculate, or answer irrelevant/personal questions.
6. Never provide answers that are not directly relevant to the project's legal data.
7. Never Give coding or technical advice unless it is strictly related to the legal context provided in this project.

---
Context: {context}
Question: {question}
'''
            # Create a RetrievalQA chain with the legal assistant prompt
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={'k': 5}),
                return_source_documents=False,
                chain_type_kwargs={'prompt': custom_prompt(template)}
            )
            
            # Get the response from the QA chain
            response = qa_chain.invoke({'query': user_input})
            answer = response["result"]
            
            # Translate the answer to Hindi if the response language is Hindi
            if language == "Hindi":
                answer = translate_text(answer, "en-IN", "hi-IN")
                
            # Display the assistant's answer in the chat
            st.chat_message("assistant").markdown(answer)
            
            # Add assistant's answer to session state
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            # Display error message in case of exception
            st.error(f"Error: {e}")

# Entry point of the Streamlit app
if __name__ == "__main__":
    main()
