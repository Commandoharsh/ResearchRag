# ResearchRAG
### Intelligent Research & Technical Knowledge Platform

ResearchRAG is an AI-powered research assistant built using Retrieval-Augmented Generation (RAG). It allows users to upload PDF documents, index their contents, and ask questions using natural language.

Instead of relying entirely on an LLM's pre-trained knowledge, ResearchRAG retrieves relevant information from uploaded documents and uses that information to generate context-aware responses.

## Key Features

- **PDF Document Ingestion:** Upload and process PDF documents.
- **Document Chunking:** Split documents into smaller text segments for retrieval.
- **Semantic Search:** Retrieve relevant content using vector embeddings.
- **Hybrid Retrieval:** Combine semantic retrieval with BM25 keyword-based retrieval.
- **Reranking:** Improve the relevance of retrieved document chunks.
- **Context Compression:** Optimize retrieved context before answer generation.
- **LLM Integration:** Support for Ollama, Google Gemini, and Mock LLM providers.
- **Streaming Responses:** Stream generated responses where supported by the application.
- **User Authentication:** User registration and login with JWT authentication.
- **Conversation Management:** Maintain conversations and message history.
- **Markdown Responses:** Render formatted AI responses in the frontend.

## Technology Stack

### Backend
- Python
- FastAPI
- Sentence Transformers
- PyTorch
- Qdrant
- BM25 (`rank-bm25`)
- SQLite
- PyPDF
- JWT Authentication

### Frontend
- React
- Vite
- JavaScript
- Axios
- React Markdown
- Remark GFM
- Lucide React

### Language Models
- Ollama — local LLM inference
- Google Gemini API — cloud LLM inference
- Mock LLM — testing and development

## Architecture

```text
                 User
                  |
                  v
           React Frontend
                  |
                  v
             FastAPI
                  |
        +---------+---------+
        |                   |
        v                   v
   Authentication      Document Upload
        |                   |
        v                   v
      SQLite            PDF Processing
                            |
                            v
                     Text Extraction
                            |
                            v
                      Text Chunking
                            |
                            v
                   Embedding Generation
                            |
                            v
                     Qdrant Vector DB
                            |
                            v
                    BM25 Indexing
                            |
                            v
                     Hybrid Retrieval
                            |
                            v
                        Reranking
                            |
                            v
                   Context Construction
                            |
                            v
                      LLM Provider
                     /     |      \
                    /      |       \
                Ollama   Gemini    Mock
                    \      |       /
                     \     |      /
                            |
                            v
                    Generated Answer
                            |
                            v
                      React Frontend
```

## Project Structure

```text
ResearchRAG/
│
├── backend/
│   ├── api/
│   │   └── routes/
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── document_repository.py
│   │   ├── document_service.py
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   └── auth_service.py
│   │
│   ├── rag/
│   │   ├── chunking/
│   │   ├── embeddings/
│   │   ├── generation/
│   │   ├── indexing/
│   │   ├── ingestion/
│   │   ├── query/
│   │   ├── retrieval/
│   │   ├── application.py
│   │   ├── application_state.py
│   │   └── rag_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── raw/
│   └── evaluation/
│
├── scripts/
├── tests/
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation and Setup

### 1. Prerequisites

Install the following:

| Software | Recommended Version |
|---|---|
| Python | 3.12 |
| Node.js | 20 LTS or newer |
| npm | Included with Node.js |
| Git | Latest stable version |
| Ollama | Latest version (optional) |

Python and Node.js can be downloaded from their official websites:

- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Git: https://git-scm.com/downloads/
- Ollama: https://ollama.com/

### 2. Clone the Repository

```bash
git clone https://github.com/Commandoharsh/rag-pipeline.git

cd rag-pipeline
```

### 3. Create a Python Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 4. Install Backend Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Install the ASGI server if it is not already installed:

```bash
pip install "uvicorn[standard]"
```

**Note:** PyTorch and Sentence Transformers are relatively large dependencies. Their installation can take some time.

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Example configuration:

```env
# ===================================
# LLM PROVIDER
# ===================================

# Supported: ollama, gemini, mock
LLM_PROVIDER=ollama


# ===================================
# OLLAMA CONFIGURATION
# ===================================

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2


# ===================================
# GEMINI CONFIGURATION
# ===================================

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

GEMINI_TIMEOUT=120


# ===================================
# RAG CONFIGURATION
# ===================================

RAG_TOP_K=5
RAG_RETRIEVAL_K=20
RAG_FINAL_K=5


# ===================================
# DOCUMENT UPLOADS
# ===================================

MAX_UPLOAD_SIZE_MB=25


# ===================================
# JWT AUTHENTICATION
# ===================================

JWT_SECRET_KEY=replace-with-a-secure-random-secret

JWT_ALGORITHM=HS256

JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Never upload your `.env` file or API keys to GitHub.

## Running ResearchRAG

ResearchRAG consists of two applications:

1. FastAPI backend.
2. React frontend.

Run them in separate terminals.

### 6. Start the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

### 7. Start the Frontend

Open another terminal:

```powershell
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Create a development environment file:

```text
frontend/.env.development
```

Add:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

The frontend should be available at:

```text
http://localhost:5173
```

Open this address in your browser.

## Configuring LLM Providers

ResearchRAG supports multiple LLM providers.

### Option 1: Ollama (Local LLM)

Ollama allows you to run language models locally without depending on a cloud LLM API.

Install Ollama:

https://ollama.com/

Download the Llama 3.2 model:

```bash
ollama pull llama3.2
```

Start Ollama:

```bash
ollama serve
```

Configure `.env`:

```env
LLM_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_MODEL=llama3.2
```

Restart the backend after changing the provider.

### Option 2: Google Gemini API

Gemini allows ResearchRAG to use Google's cloud-hosted language models.

Obtain an API key through Google AI Studio:

https://aistudio.google.com/apikey

Configure `.env`:

```env
LLM_PROVIDER=gemini

GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=gemini-2.5-flash

GEMINI_TIMEOUT=120
```

Restart the backend.

**Security:** Keep your Gemini API key private. Do not expose it in frontend environment variables or commit it to Git.

### Option 3: Mock Provider

The Mock provider is useful for development and testing without making external LLM requests.

Configure:

```env
LLM_PROVIDER=mock
```

Restart the backend.

## How to Use

### 1. Register or Log In

Open the frontend and create an account.

Log in using your registered credentials.

### 2. Upload a PDF

Navigate to the document upload section.

Select a PDF file and upload it.

The application processes the PDF through its indexing pipeline.

### 3. Document Indexing

The backend performs the following operations:

1. Extract text from the PDF.
2. Split the extracted text into chunks.
3. Generate embeddings.
4. Store vectors and metadata in Qdrant.
5. Build the BM25 keyword index.
6. Register document information in SQLite.

### 4. Ask Questions

Navigate to the chat interface.

Ask questions related to your uploaded documents.

ResearchRAG retrieves relevant information and sends the retrieved context to the configured LLM provider.

The generated answer is returned to the frontend.

### 5. Continue Conversations

Use the conversation interface to maintain and continue previous discussions.

## Testing

Activate the Python virtual environment.

From the project root:

```bash
pytest
```

For more detailed test output:

```bash
pytest -v
```

To run a particular test file:

```bash
pytest tests/test_example.py -v
```

Replace the example filename with an actual test file in your repository.

## Frontend Build

To create a production frontend build:

```bash
cd frontend

npm run build
```

To preview the production build locally:

```bash
npm run preview
```

## Data Storage

The current local development configuration uses:

| Component | Storage |
|---|---|
| User accounts | SQLite |
| Conversations | SQLite |
| Messages | SQLite |
| Document metadata | SQLite |
| Document vectors | Embedded Qdrant |
| Uploaded PDFs | Local filesystem |
| BM25 index | Rebuilt from stored vector payloads |

Important local data directories:

```text
data/
├── raw/
├── qdrant/
└── researchrag.db
```

These directories contain application data and should not be committed to Git.

## Troubleshooting

### Backend cannot find a Python module

Ensure your virtual environment is activated.

Run commands from the repository root:

```powershell
cd C:\Users\harsh\ResearchRAG

.\.venv\Scripts\Activate.ps1
```

### Ollama connection error

Check whether Ollama is running:

```bash
ollama list
```

Verify the configured URL:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

### Gemini API error

Check:

- The API key is configured correctly.
- The selected model is available to your API key.
- Your API quota has not been exceeded.
- Your internet connection is working.

### Frontend cannot connect to backend

Verify that:

- The backend is running on port 8000.
- The frontend API URL points to the correct backend.
- The backend CORS configuration permits the frontend origin.

### Qdrant database lock error

Embedded Qdrant uses a local storage lock.

Avoid starting multiple backend processes against the same `data/qdrant` directory. Stop the previous backend process before restarting it.

Do not delete the Qdrant directory to resolve a lock error, as it contains indexed document data.

## Current Development Status

ResearchRAG is an actively developed project.

Implemented capabilities include:

- PDF ingestion and indexing.
- Semantic retrieval.
- BM25 keyword retrieval.
- Hybrid retrieval.
- Reranking.
- Context-aware answer generation.
- Ollama integration.
- Google Gemini integration.
- JWT authentication.
- Conversation management.
- React-based chat interface.

Cloud database, persistent object storage, and production deployment configurations are part of the ongoing development roadmap.

## Future Improvements

- Cloud-based vector database integration.
- PostgreSQL/Supabase database migration.
- Persistent cloud document storage.
- Production deployment.
- Improved retrieval evaluation.
- Advanced citation and source attribution.
- Multi-document reasoning.
- Improved observability and performance optimization.

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Run the relevant tests.
5. Submit a pull request.

## License

Add a license to this repository before distributing or reusing the project under specific open-source terms.

---

**ResearchRAG**  
An intelligent research assistant powered by Retrieval-Augmented Generation.