from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, Http404
import json
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
DB_FAISS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vectorstore/db_faiss'))
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))

# Check if FAISS index exists before loading
faiss_index_exists = os.path.exists(os.path.join(DB_FAISS_PATH, 'index.faiss')) and os.path.exists(os.path.join(DB_FAISS_PATH, 'index.pkl'))

if faiss_index_exists:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = ChatNVIDIA(
        model="mistralai/mistral-7b-instruct-v0.3",
        api_key=NVIDIA_API_KEY,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )
    prompt = PromptTemplate(
        template="""
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
""",
        input_variables=["context", "question"]
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={'k': 5}),
        chain_type_kwargs={"prompt": prompt}
    )
else:
    embeddings = None
    vectorstore = None
    llm = None
    prompt = None
    qa = None

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

def index(request):
    # List all files in data/ and vectorstore/db_faiss/
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith('.pdf')]
    faiss_files = os.listdir(DB_FAISS_PATH) if os.path.exists(DB_FAISS_PATH) else []
    faiss_ready = faiss_index_exists
    return render(request, 'web_lawgic/index.html', {
        'pdf_files': pdf_files,
        'faiss_files': faiss_files,
        'faiss_ready': faiss_ready,
    })

@csrf_exempt
def chat(request):
    if not faiss_index_exists or qa is None:
        return JsonResponse({'reply': 'Vectorstore is missing. Please run: python chatbot/create_memory.py'})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            language = data.get('language', 'English')
            if not user_message:
                return JsonResponse({'reply': 'Please enter a question.'})
            query = user_message
            # If Hindi, translate to English for processing
            if language == 'Hindi':
                # Use your translation logic or a placeholder
                query = user_message  # Add translation if you want
            result = qa.invoke({"query": query})
            answer = result.get('result', 'Sorry, I could not find an answer.')
            # If Hindi, translate back
            if language == 'Hindi':
                # Use your translation logic or a placeholder
                answer = answer  # Add translation if you want
            return JsonResponse({'reply': answer})
        except Exception as e:
            return JsonResponse({'reply': f'[Error] {str(e)}'})
    return JsonResponse({'reply': 'Invalid request.'})

def list_files(request):
    # Return all files in data/ and vectorstore/db_faiss/ as JSON
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith('.pdf')]
    faiss_files = os.listdir(DB_FAISS_PATH) if os.path.exists(DB_FAISS_PATH) else []
    return JsonResponse({'pdf_files': pdf_files, 'faiss_files': faiss_files})

def download_file(request, folder, filename):
    # Allow download of any file in data/ or vectorstore/db_faiss/
    if folder == 'data':
        file_path = os.path.join(DATA_PATH, filename)
    elif folder == 'vectorstore':
        file_path = os.path.join(DB_FAISS_PATH, filename)
    else:
        raise Http404()
    if not os.path.exists(file_path):
        raise Http404()
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
