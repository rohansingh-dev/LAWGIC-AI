# Lawgic Unified Project

This project combines a Django web backend and a Streamlit-based RAG chatbot for legal Q&A, using a shared vectorstore and data folder.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Copy your PDFs to `data/`**
   - Add as many high-quality legal PDFs as possible (laws, case studies, government guides, etc.)
3. **Create the vectorstore**
   ```bash
   python chatbot/create_memory.py
   ```
   - Re-run this command every time you add new PDFs.
4. **Run the Django web app**
   ```bash
   cd lawgic
   python manage.py runserver
   ```
5. **(Optional) Run the Streamlit chatbot**
   ```bash
   streamlit run chatbot/chatbot.py
   ```

## Configuration
- Set your HuggingFace API key in a `.env` file (see `.env.example`).
- Both the chatbot and backend use the same vectorstore and data.

## Usage
- Open your browser at [http://localhost:8000/](http://localhost:8000/) to use the Lawgic AI Chatbot.
- Type your legal question in the chat interface and get instant, safe, and clear answers.
- Use the language selector for English or Hindi (translation supported if API key is set).

## Best Practices
- **Add more legal data:** The more legal PDFs you add, the better the answers.
- **Keep your vectorstore up to date:** Always re-run the vectorstore creation script after adding new data.
- **Use open-access models:** For best compatibility and no API restrictions.
- **Review and improve prompts:** Prompts are tuned for safety and clarity, but you can further refine them for your needs.

## Structure
- `data/` — Your legal PDFs
- `vectorstore/db_faiss/` — FAISS vector index
- `chatbot/` — Scripts for vectorstore creation and Streamlit UI
- `lawgic/` — Django backend and chatbot UI

---
**Note:** Both Django and Streamlit chatbots are fully supported and share the same backend data.

## Changes
- NVIDIA LLM API via langchain-nvidia-ai-endpoints is now used for all legal question answering (no HuggingFace API required for LLM)
- Add your NVIDIA API key to .env as NVIDIA_API_KEY
- See https://docs.api.nvidia.com/nim/reference/llm-apis for more info
