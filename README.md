# RAG-Agent: Intelligent Document Assistant

## What is this project about?
This project is a complete, full-stack Retrieval-Augmented Generation (RAG) application. It allows users to upload PDF or text documents to train a local AI assistant instantly. Once a document is ingested, the user can chat with an autonomous AI agent that intelligently searches the uploaded documents to provide accurate, context-aware answers.

## Tools Used
- **Orchestration & Logic:** n8n (Self-hosted via Docker)
- **Vector Database (Memory):** Qdrant (Self-hosted via Docker)
- **Intelligence & Embeddings:** Google Gemini APIs (`gemini-1.5-flash`/`pro` for conversational generation, and `gemini-embeddings-2-preview` for vectorization)
- **Frontend Interface:** Streamlit (Python)

---

## How it was Built (Architecture)

### 1. Infrastructure Setup
The backend infrastructure relies on a `docker-compose.yml` file to spin up two lightweight containers: **n8n** (port 5678) and **Qdrant** (port 6333). Running them on the same Docker network allows n8n to communicate with Qdrant securely without exposing the database to the internet.

### 2. Workflow 1: Document Ingestion
When a user uploads a document in the Streamlit UI, it triggers the first n8n pipeline:
1. **Webhook Node:** Receives the file via a standard HTTP POST request.
2. **Document Processing:** n8n extracts the raw text from the PDF and splits it into manageable chunks (1000 characters with a 200-character overlap).
3. **Embeddings:** The chunks are sent to the Gemini Embeddings API, which converts the human text into mathematical vectors.
4. **Vector Storage:** The vectors (and the original text chunks) are saved into a Qdrant collection named `rag-docs`.

### 3. Workflow 2: Retrieval & Chat Agent
When a user asks a question in the Streamlit UI, it triggers the second n8n pipeline:
1. **Webhook Node:** Receives the user's text query and a unique Session ID.
2. **AI Agent Node:** An autonomous LangChain-style agent receives the query. It is equipped with **Simple Memory** (to remember the conversation history mapped to the Session ID) and a **Vector Store Tool**.
3. **Retrieval Tooling:** The agent determines if it needs to search the documents to answer the question. If so, it uses the Vector Store Tool to search Qdrant for chunks of text that mathematically match the user's question.
4. **Generation:** The agent passes the retrieved context to the Gemini Chat Model, which formulates a natural, accurate response and sends it back to the Streamlit UI.

---

## Troubleshooting Guide

During the development of this architecture, several critical hurdles were encountered and resolved. If you are rebuilding or modifying this stack, reference the following solutions:

### 1. n8n Login Loop over VPNs (Tailscale)
**Symptom:** When accessing the n8n dashboard via a Tailscale IP or reverse proxy over HTTP, n8n throws a "secure cookie" error and refuses to log you in.
**Fix:** Add `- N8N_SECURE_COOKIE=false` to the environment variables in your `docker-compose.yml` file and recreate the container.

### 2. Browser "GET" Errors on Webhooks
**Symptom:** Testing the n8n Webhook by pasting its URL into a Chrome/Safari address bar returns: *"This webhook is not registered for GET requests."*
**Fix:** This is expected behavior. Web browsers send `GET` requests by default. The Ingestion webhook is configured exclusively for `POST` requests to accept file payloads. You must test the webhook using the Streamlit app or an API client like Postman.

### 3. Agent Fails with "Invalid String" Error
**Symptom:** The AI Agent throws an error: *"I'm sorry, I cannot process that input. Please provide a valid string to search for."*
**Fix:** This occurs when the Streamlit JSON payload is deeply nested (e.g., inside a `body` object) but the Agent is configured to read the root. Update the Agent's Prompt expression to correctly map the payload: `={{ $json.body.query }}`.

### 4. Agent Refuses to Access Documents
**Symptom:** The AI responds perfectly, but says: *"I don't have access to the document you uploaded. My capabilities are limited to the tools provided..."*
**Fix:** The Agent does not inherently know what the Qdrant database is for. 
1. You must use a **Vector Store Question Answer Tool** (or standard Vector Store Tool) to connect Qdrant to the Agent.
2. **Crucially**, you must write an explicit description inside the tool settings: *"Use this tool to search the contents of the user's uploaded documents."* Without this description, the LLM will ignore the database entirely.

### 5. Agent Searches but Returns Zero Results (Silent Failure)
**Symptom:** The AI Agent attempts to use the search tool, but states it couldn't find any relevant information, even though documents were successfully ingested.
**Fix:** Check your Embedding Models. The model used to vectorize the text in the Ingestion workflow (e.g., `gemini-embeddings-2-preview`) **must perfectly match** the model used to search the database in the Retrieval workflow. If they do not match, the vector dimensions will be incompatible, resulting in a silent search failure yielding 0 results.