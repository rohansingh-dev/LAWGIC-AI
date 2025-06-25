# LawgicAI

LawgicAI is an AI-powered legal assistant focused on Indian law. It provides instant, context-aware answers to legal questions, document search, and multilingual support, all with a modern web interface.

---

## 🚀 Features
- **Instant Legal Q&A**: Get answers to your legal questions based on Indian law, powered by advanced AI and real legal documents.
- **Multilingual Support**: Ask questions in English or Hindi. Switch language instantly in the chatbot UI.
- **PDF Document Ingestion & Search**: Upload and search Indian legal PDFs. The system indexes and retrieves relevant content for your queries.
- **User Chat History**: Authenticated users have their chat history saved and can view past questions and answers.
- **Offline Translation**: Uses Argos Translate for secure, offline translation (Python 3.10/3.11 required).
- **Modern Web UI**: Responsive, accessible interface built with Django and Tailwind CSS.
- **Community & Contact Pages**: Connect with legal professionals and the LawgicAI team.

---

## 🛠️ Tech Stack
- **Backend**: Django 5, Python 3.10/3.11
- **AI/ML**: LangChain, FAISS, HuggingFace Transformers
- **Vector Store**: FAISS (local, fast retrieval)
- **Translation**: Argos Translate (offline, privacy-friendly)
- **Frontend**: Tailwind CSS, FontAwesome, Responsive HTML

---

## ⚡ Quickstart

### 1. Prerequisites
- Python 3.10 or 3.11 (required for Argos Translate)
- Git

### 2. Clone the Repository
```sh
git clone <your-repo-url>
cd lawgic_unified
```

### 3. Create and Activate a Virtual Environment
```sh
python3.11 -m venv venv311
venv311\Scripts\activate  # On Windows
# or
source venv311/bin/activate  # On Linux/Mac
```

### 4. Install Dependencies
```sh
pip install -r requirements.txt
```

### 5. Environment Variables
Create a `.env` file in the project root with your HuggingFace and NVIDIA API keys:
```
HF_TOKEN="your_huggingface_token"
NVIDIA_API_KEY="your_nvidia_api_key"
```

### 6. Database Migrations
```sh
python lawgic/manage.py migrate
```

### 7. Ingest Legal PDFs (Optional, for document search)
```sh
python chatbot/create_memory.py
```

### 8. Run the Development Server
```sh
python lawgic/manage.py runserver
```

---

## 🖥️ Usage
- Access the app at *http://127.0.0.1:8000/* (When host locally)**
- Use the chatbot for legal Q&A (English/Hindi)
- View your chat history (collapsible section in chatbot page)
- Download legal documents from the files section
- Explore features, community, and contact pages

---

## 📝 Project Structure
```
lawgic_ai/
├── chatbot/                # PDF ingestion and vectorstore creation
├── data/                   # Legal PDF files
├── lawgic/                 # Django project
│   ├── lawgic/             # Django settings, URLs
│   └── web_lawgic/         # Main app: views, templates, models
├── vectorstore/            # FAISS vector index
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .env                    # API keys (not committed)
```

---

## 🌐 Translation
- Uses Argos Translate for offline, secure translation (Python 3.10/3.11 only)
- First translation may take time as language models are downloaded automatically

---

## 🔒 Security & Privacy
- All chat history is stored locally and only accessible to the authenticated user
- No personal data is shared with third parties
- Translation and vector search are performed offline where possible

---

## 📄 License
This project is open source and available under the MIT License.

---

## 🤝 Contributing
Pull requests and suggestions are welcome! Please open an issue or submit a PR.

---

## 🙏 Acknowledgements
- [Django](https://www.djangoproject.com/)
- [LangChain](https://www.langchain.com/)
- [HuggingFace](https://huggingface.co/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Argos Translate](https://www.argosopentech.com/)
- [NividaNim](https://build.nvidia.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

For questions or support, contact the LawgicAI Dev Team via the Contact page.

