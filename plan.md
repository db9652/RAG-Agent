# RAG-Agent Project Plan

## Objective
Build a complete RAG (Retrieval-Augmented Generation) agent with a web interface for document uploads and chatting, orchestrated by n8n and powered by Google Gemini APIs.

## Architecture
- **Frontend (UI & Client):** Streamlit (Python app running locally on port 8501)
- **Orchestration & Backend:** n8n (running in Docker on port 5678)
- **Vector Database (Memory):** Qdrant (running alongside n8n in Docker on port 6333)
- **LLM Engine:** Google Gemini (1.5 models for generation, text-embedding models for vectorization)

## Phases
1. **[X] Phase 1: Infrastructure Setup**
   - Create `docker-compose.yml` (n8n + Qdrant).
   - Verify both services are running locally.
2. **[X] Phase 2: Backend Logic (n8n Workflows)**
   - **Ingestion Workflow:** Receive a document via Webhook → Extract text → Chunk text → Generate Gemini Embeddings → Store in Qdrant. *(Completed)*
   - **Retrieval & Chat Workflow:** Receive user query via Webhook → Generate Gemini Embedding for query → Search Qdrant for similar chunks → Send context + query to Gemini 1.5 → Return response to Frontend. *(Completed)*
3. **[X] Phase 3: Frontend Development (Streamlit)**
   - Build a file uploader sidebar for PDF/text ingestion. *(Completed)*
   - Build a main chat interface for the user to ask questions. *(Completed)*
   - Connect the UI to the n8n Webhooks via HTTP requests. *(Completed)*
4. **[X] Phase 4: Testing & Refinement**
   - End-to-end testing with sample documents. *(Completed)*
   - Refine chunk sizes and prompt engineering. *(Completed)*

5. **[ ] Phase 5: Production Readiness & Advanced Features**
   - **Hybrid Search**: Combine semantic search with keyword matching (BM25) for specialized terminology.
   - **Batch Processing**: Support uploading and processing multiple documents simultaneously.
   - **Source Citations**: Update the UI to show precisely which document snippets were used to generate the answer.
   - **Evaluation Framework**: Integrate `Ragas` to automatically evaluate answer faithfulness and relevance.

## Future Upgrades
- **GraphRAG (LightRAG)**: Integrate HKUDS LightRAG to allow the agent to reason about document relationships, not just content.
- **Local LLM Integration**: Add a toggle to use `Ollama` (Llama 3 / Mistral) for 100% offline, private document processing.
- **Multimodal Support**: Expand ingestion to handle images and charts within documents using Gemini Pro Vision.