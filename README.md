# Lawgic Unified Project

Lawgic Unified is an AI-powered legal Q&A platform combining a Django web backend and a Streamlit-based chatbot UI. Both interfaces use a shared vectorstore and data folder for seamless, consistent answers.

## Features
- **Unified backend:** Django web app and Streamlit chatbot share the same vectorstore and legal data.
- **RAG (Retrieval-Augmented Generation):** Answers are grounded in your uploaded legal PDFs.
- **NVIDIA LLM API:** Uses NVIDIA's LLM API for all legal question answering (no HuggingFace LLM required for LLM).
- **Multi-language support:** English and Hindi (translation if HuggingFace API key is set).
- **Easy extensibility:** Add more legal PDFs to improve answer quality.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Add your legal PDFs**
   - Place high-quality legal PDFs (laws, case studies, government guides, etc.) in the `data/` folder.
3. **Create or update the vectorstore**
   ```bash
   python chatbot/create_memory.py
   ```
   - Re-run this command every time you add new PDFs.
4. **Configure API keys**
   - Copy `.env.example` to `.env` and set your keys:
     - `NVIDIA_API_KEY` (required for LLM)
     - `HF_TOKEN` (optional, for translation)
5. **Run the Django web app**
   ```bash
   cd lawgic
   python manage.py runserver
   ```
   - Access at [http://localhost:8000/](http://localhost:8000/)
6. **(Optional) Run the Streamlit chatbot**
   ```bash
   streamlit run chatbot/chatbot.py
   ```

## Configuration
- `.env` file in the project root holds your API keys.
- Both Django and Streamlit use the same vectorstore and data.

## Usage
- Ask legal questions via the web UI or Streamlit chatbot.
- Answers are based on your uploaded PDFs and NVIDIA LLM.
- Use the language selector for English or Hindi.

## Best Practices
- **Add more legal data:** The more legal PDFs you add, the better the answers.
- **Keep your vectorstore up to date:** Always re-run the vectorstore creation script after adding new data.
- **Use open-access models:** For best compatibility and no API restrictions.
- **Review and improve prompts:** Prompts are tuned for safety and clarity, but you can further refine them for your needs.

## Project Structure
- `data/` — Your legal PDFs
- `vectorstore/db_faiss/` — FAISS vector index
- `chatbot/` — Scripts for vectorstore creation and Streamlit UI
- `lawgic/` — Django backend and chatbot UI

---
**Note:** Both Django and Streamlit chatbots are fully supported and share the same backend data and vectorstore.

## Changes & API Info
- **NVIDIA LLM API** via `langchain-nvidia-ai-endpoints` is now used for all legal question answering.
- Add your NVIDIA API key to `.env` as `NVIDIA_API_KEY`.
- See [NVIDIA LLM API docs](https://docs.api.nvidia.com/nim/reference/llm-apis) for more info.

## Troubleshooting
- If you see errors about missing API keys, check your `.env` file.
- If answers seem outdated, re-run the vectorstore creation script after adding new PDFs.
- For any issues with dependencies, ensure your Python version is compatible and all packages are installed from `requirements.txt`.
