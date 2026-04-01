# Implementation Details

## Environment Setup
- **Workspace:** `/home/white/ai/RAG-Agent`
- **Python Virtual Environment:** `/home/white/ai/venv`
- **Docker:** Installed natively.

## Component Specifications

### 1. Docker Compose (n8n + Qdrant)
*(Pending creation of docker-compose.yml)*

### 2. Python Dependencies
*(Pending creation of requirements.txt)*
Expected packages:
- `streamlit`
- `requests`
- `python-dotenv`

### 3. n8n API Contracts

**Webhook 1: Document Ingestion**
- **Method:** POST
- **URL:** *(Awaiting User Input)*
- **Payload:** Multipart Form-Data (File upload) with the key `data`

**Webhook 2: Chat & Retrieval**
- **Method:** POST
- **URL:** *(TBD)*
- **Payload:** 
  ```json
  {
    "sessionId": "string",
    "query": "string"
  }
  ```
- **Response:**
  ```json
  {
    "answer": "string",
    "sources": ["list of strings"]
  }
  ```

## API Keys Required
- `GEMINI_API_KEY`: Required in n8n for LLM and Embedding nodes.