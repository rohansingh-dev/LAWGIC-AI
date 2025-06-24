from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
import json
import requests
import argostranslate.package, argostranslate.translate
from .models import ChatMessage


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
DB_FAISS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vectorstore/db_faiss'))
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "mistralai/mistral-7b-instruct-v0.3"

faiss_index_exists = os.path.exists(os.path.join(DB_FAISS_PATH, 'index.faiss')) and os.path.exists(os.path.join(DB_FAISS_PATH, 'index.pkl'))

if faiss_index_exists:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        max_new_tokens=512
    )
    prompt = PromptTemplate(
        template="""
You are LawgicAI, a professional assistant specializing in Indian law. Your responses must always:

- Be strictly based on the provided legal context (Indian laws, acts, case studies, government documents, etc.).
- Be clear, concise, and professional:
    - Use bullet points for lists, steps, or key facts.
    - Use short paragraphs for explanations or context.
    - Combine both formats for clarity and readability.
- Use simple, direct language suitable for the general public.
- Avoid repetition, filler, or speculation.
- Remain neutral, objective, and free from personal opinions.
- Reference relevant laws, sections, or context when possible.

**Instructions:**
1. If the user's message is a greeting or small talk, reply with:
    - "Hello! I can assist you with Indian legal matters. Please ask your legal question."
    - "For emergencies or crimes, contact local law enforcement immediately."
    - "I provide general legal information, not legal advice or emergency help."
    - Do not engage in small talk for more than two prompts per user.
2. If the user's message is not clearly about Indian law, legal rights, legal procedures, or legal topics, reply only with:
    - "I can only assist with questions related to Indian legal matters."
    - "For emergencies or crimes, contact local law enforcement immediately."
    - "I provide general legal information, not legal advice or emergency help."
    - "No response will be given to non-legal, personal, or irrelevant queries."
3. If the answer is not found in the provided context, reply only with:
    - "I could not find a specific answer in the provided Indian legal context."
    - "Please consult a qualified legal professional for further assistance."
4. For valid legal questions:
    - Start with a brief summary (1-2 sentences) if appropriate.
    - Follow with clear, well-organized bullet points for steps, requirements, or key facts.
    - Reference the context or law section if possible.
    - Use simple, direct language.
    - Avoid unnecessary repetition or filler.
5. Never make up information, speculate, or answer irrelevant/personal questions.

---
Context: {context}
Question: {question}
""",
        input_variables=["context", "question"]
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True,
        chain_type_kwargs={'prompt': prompt}
    )
else:
    embeddings = None
    vectorstore = None
    llm = None
    prompt = None
    qa_chain = None

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'web_lawgic/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'web_lawgic/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    return render(request, 'web_lawgic/home.html')

@login_required
def features(request):
    return render(request, 'web_lawgic/features.html')

@login_required
def community(request):
    return render(request, 'web_lawgic/community.html')

@login_required
def contact(request):
    return render(request, 'web_lawgic/contact.html')

@login_required
def chatbot(request):
    return render(request, 'web_lawgic/chatbot.html')

def translate_text(text, source_lang, target_lang, *_args, **_kwargs):

    lang_map = {
        'english': 'en', 'en': 'en',
        'hindi': 'hi', 'hi': 'hi',
    }
    src = lang_map.get(source_lang.lower(), source_lang[:2].lower())
    tgt = lang_map.get(target_lang.lower(), target_lang[:2].lower())
    if src == tgt:
        return text
    try:
        installed = argostranslate.package.get_installed_packages()
        if not any(p.from_code == src and p.to_code == tgt for p in installed):
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()
            pkg = next((p for p in available if p.from_code == src and p.to_code == tgt), None)
            if pkg:
                argostranslate.package.install_from_path(pkg.download())
            else:
                return f"[Translation Error: No Argos package for {src}->{tgt}]"
        if isinstance(text, str):
            if not text.strip():
                return '[Translation Error: Empty input]'
            return argostranslate.translate.translate(text, src, tgt)
        elif isinstance(text, list):
            if not text or not any(t.strip() for t in text):
                return '[Translation Error: Empty input]'
            return [argostranslate.translate.translate(t, src, tgt) for t in text]
        else:
            return '[Translation Error: Invalid input type]'
    except Exception as e:
        return f"[Translation Error: {str(e)}]"

@csrf_exempt
def chat(request):
    if not faiss_index_exists:
        return JsonResponse({'reply': 'Vectorstore is missing. Please run: python chatbot/create_memory.py'}, status=500)
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        language = data.get('language', 'English')
        context = ""
        try:
            if qa_chain:
                retrieved = qa_chain.retriever.invoke(user_message)
                context = "\n".join([doc.page_content for doc in retrieved])
            prompt_text = prompt.format(context=context, question=user_message) if prompt else user_message
            if language.lower().startswith('hi'):
                user_message_en = translate_text(user_message, 'hi', 'en')
                prompt_text = prompt.format(context=context, question=user_message_en) if prompt else user_message_en
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": NVIDIA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt_text}
                ],
                "max_tokens": 512,
                "temperature": 0.5
            }
            response = requests.post(NVIDIA_NIM_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            answer = result['choices'][0]['message']['content']
            if language.lower().startswith('hi'):
                answer = translate_text(answer, 'en', 'hi')
            # Save chat history if user is authenticated
            if request.user.is_authenticated:
                ChatMessage.objects.create(user=request.user, question=user_message, answer=answer)
        except Exception as e:
            answer = '[Error] ' + str(e)
        return JsonResponse({'reply': answer})
    return JsonResponse({'reply': 'Invalid request.'}, status=400)

@login_required
def chat_history(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50]
    history = [
        {
            'question': msg.question,
            'answer': msg.answer,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ]
    return JsonResponse({'history': history})

@login_required
def list_files(request):
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith('.pdf')]
    faiss_files = os.listdir(DB_FAISS_PATH) if os.path.exists(DB_FAISS_PATH) else []
    return JsonResponse({'pdf_files': pdf_files, 'faiss_files': faiss_files})

@login_required
def download_file(request, folder, filename):
    if folder == 'data':
        file_path = os.path.join(DATA_PATH, filename)
    elif folder == 'vectorstore':
        file_path = os.path.join(DB_FAISS_PATH, filename)
    else:
        raise Http404()
    if not os.path.exists(file_path):
        raise Http404()
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

@login_required
def about(request):
    return render(request, 'web_lawgic/about.html')
