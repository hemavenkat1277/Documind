Distributed RAG Platform for Enterprise Knowledge Search

This is the project I would put on a resume for an Applied AI role.

Problem Statement

Organizations have thousands of documents:

PDFs
Technical Manuals
SOPs
HR Policies
API Documentation
Research Reports

Traditional keyword search often fails because users ask questions in natural language.

Build a Distributed Retrieval-Augmented Generation (RAG) Platform that allows users to upload documents and ask questions in natural language while providing source citations and evaluation metrics.

System Goals

The platform should:

Document Processing
Upload documents
Extract text
Generate metadata
Create embeddings
Store vectors
Intelligent Search
Semantic Search
Metadata Filtering
Hybrid Retrieval
Question Answering
Context Retrieval
LLM Response Generation
Source Citation
Evaluation
Retrieval Quality
Hallucination Detection
Response Faithfulness
Monitoring
Query Latency
Embedding Costs
Model Usage
Architecture
                    ┌──────────────┐
                    │    Client    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ API Gateway  │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼

 ┌────────────┐    ┌─────────────┐    ┌─────────────┐
 │ Document   │    │ Search      │    │ Chat        │
 │ Service    │    │ Service     │    │ Service     │
 └─────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  │                  │
            ┌─────▼──────────────────▼─────┐
            │      Redis Queue             │
            └─────┬──────────────────┬─────┘
                  │                  │
          ┌───────▼──────┐    ┌──────▼──────┐
          │ Chunk Worker │    │ Embed Worker│
          └───────┬──────┘    └──────┬──────┘
                  │                  │
          ┌───────▼──────┐    ┌──────▼──────┐
          │ PostgreSQL   │    │ Qdrant      │
          └──────────────┘    └─────────────┘
Core Services
1. API Gateway

Acts as the entry point.

Responsibilities:

Authentication
Routing
Rate Limiting
Request Validation

Endpoints:

POST /upload
POST /chat
GET /documents
GET /metrics
2. Document Service

Responsible for document management.

Upload Flow
Upload PDF
     ↓
Store Metadata
     ↓
Send Job To Queue
     ↓
Return Document ID
Database
documents

id
name
owner_id
status
created_at

Status:

UPLOADED
PROCESSING
INDEXED
FAILED
3. Chunking Worker

Runs asynchronously.

Responsibilities
Read document
Extract text
Split text
Store chunks
Example
100 page PDF
       ↓
Extract text
       ↓
400 chunks
       ↓
Store in database

Chunk table:

chunks

id
document_id
chunk_text
page_number
section
4. Embedding Service

Consumes chunk jobs.

Workflow
Chunk Created
      ↓
Generate Embedding
      ↓
Store Vector

Model:

BAAI/bge-small-en-v1.5

Vector Size:

384
5. Vector Database

Use:

Preferred

Qdrant

Stores:

{
  "vector":[...],
  "document_id":1,
  "chunk_id":55,
  "page":12
}

Supports:

Similarity Search
Metadata Filters
Top-K Retrieval
6. Search Service

Query Flow:

User Query
      ↓
Embedding Generation
      ↓
Vector Search
      ↓
Top 10 Chunks
      ↓
Re-ranking
      ↓
Top 5 Chunks
Re-ranking

Use:

cross-encoder/ms-marco-MiniLM

This dramatically improves retrieval quality.

7. Chat Service

Receives:

{
  "question":"How does leave policy work?"
}

Workflow:

Question
    ↓
Retrieve Context
    ↓
Build Prompt
    ↓
Call LLM
    ↓
Generate Answer

Model:

Use:

Ollama

Run:

Llama 3.1 8B
Qwen 3
8. Evaluation Service

This is the feature that makes the project stand out.

Most student projects stop at answering questions.

You will evaluate answers.

Metrics
Retrieval
Precision@K
Recall@K
MRR
Generation
Faithfulness
Answer Relevance
Context Relevance

Use:

Ragas

Store:

evaluations

id
query
faithfulness
relevance
latency
created_at
Database Design
PostgreSQL
documents
id
name
owner
status
created_at
chunks
id
document_id
chunk_text
page_number
section
queries
id
user_id
query
response
latency
created_at
evaluations
id
query_id
faithfulness
relevance
precision
Folder Structure
distributed-rag/

backend/
│
├── gateway/
│
├── document_service/
│
├── search_service/
│
├── chat_service/
│
├── evaluation_service/
│
├── workers/
│   ├── chunk_worker.py
│   └── embedding_worker.py
│
├── database/
│
├── vector_store/
│
├── models/
│
├── tests/
│
└── docker-compose.yml