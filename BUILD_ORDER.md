# DocuMind Build Order

Use this guide when you rebuild DocuMind from scratch in another folder. Build each step, understand what it does, run it if possible, then move to the next step.

## Short Version

```text
config -> schema -> db -> LangChain services -> kafka -> schemas -> api -> worker -> docker -> tests
```

Do not start with Docker or FastAPI first. Start with the database schema and small service functions, because those are the foundation of the whole project.

## 1. Project Setup

Create these files first:

- `requirements.txt`
- `.env.example`
- `.gitignore`

Goal: define the libraries, environment variables, and ignored local files.

You should understand:

- Which Python packages are needed.
- Which LangChain packages are used: `langchain-core` and `langchain-text-splitters`.
- Which Hugging Face packages are used: `langchain-huggingface` and `sentence-transformers`.
- Which services the app depends on: PostgreSQL, Redis, Kafka/Redpanda.
- Which files should not be committed, such as `.env`, `.venv`, cache files, and uploaded documents.

## 2. Configuration

Create:

- `app/config.py`

Goal: load all important settings from environment variables.

This file should manage:

- Database URL
- Kafka bootstrap servers
- Redis URL
- Upload directory
- Embedding dimension
- Chunk size
- Chunk overlap
- Retrieval limits
- Cache TTL

## 3. Database Schema

Create:

- `app/sql/schema.sql`

Build the tables in this order:

1. `documents`
2. `chunks`
3. `pipeline_events`
4. `retrieval_events`

Goal: understand what data the system stores before writing the API or worker.

Important concepts:

- `documents` stores uploaded file metadata and processing status.
- `chunks` stores split document text and vector embeddings.
- `pipeline_events` logs asynchronous ingestion stages.
- `retrieval_events` stores query latency, relevance score, cache usage, and answer metrics.
- `pgvector` enables semantic similarity search inside PostgreSQL.

## 4. Database Connection

Create:

- `app/db.py`

Goal: connect Python code to PostgreSQL and initialize the schema.

This file should provide:

- A shared async connection pool.
- A function to run `schema.sql`.
- A FastAPI dependency for getting a database connection.
- Pool startup and shutdown helpers.

## 5. Core LangChain RAG Utilities

Create these before the API and worker:

- `app/services/text_extraction.py`
- `app/services/chunking.py`
- `app/services/embeddings.py`

Goal: build the basic LangChain-powered document processing pipeline.

Build them in this order:

1. `text_extraction.py`
   Extract text from `.txt`, `.md`, `.pdf`, and `.docx` files.

2. `chunking.py`
   Convert text into LangChain `Document` objects and split them with `RecursiveCharacterTextSplitter`.

3. `embeddings.py`
   Configure LangChain `HuggingFaceEmbeddings` with `BAAI/bge-small-en-v1.5` and convert text chunks into vector embeddings.

At this point, you should be able to go from:

```text
uploaded file -> extracted text -> LangChain Documents -> chunks -> LangChain embeddings
```

## 6. Retrieval Logic

Create:

- `app/services/reranker.py`
- `app/services/retrieval.py`
- `app/services/llm.py`
- `app/services/evaluation.py`

Build them in this order:

1. `reranker.py`
   Score query and context pairs after vector search with a Transformers cross-encoder model.

2. `retrieval.py`
   Embed the question, search PostgreSQL with pgvector, and rerank candidate chunks.

3. `llm.py`
   Generate an answer from the retrieved context using a LangChain runnable chain.

4. `evaluation.py`
   Record latency, top retrieval score, cache usage, and answer length.

Goal: make the query side of RAG work.

At this point, the query flow should be:

```text
question -> question embedding -> pgvector search -> reranking -> answer -> metrics
```

## 7. Kafka Helper

Create:

- `app/kafka_bus.py`

Goal: define Kafka topics and reusable producer/consumer helpers.

Topics:

- `document.uploaded`
- `chunks.created`
- `embeddings.created`
- `vector.indexed`

This file should keep Kafka code separate from both the API and worker.

## 8. API Schemas

Create:

- `app/schemas.py`

Goal: define request and response models.

Models to create:

- Document upload response
- Document status response
- Query request
- Retrieved chunk
- Query response
- Retrieval metric

This makes the API predictable and keeps validation separate from endpoint logic.

## 9. FastAPI App

Create:

- `app/main.py`

Build endpoints in this order:

1. `GET /health`
   Check database and Redis connectivity.

2. `POST /documents`
   Accept file uploads, save the file, insert a document row, and publish a Kafka event.

3. `GET /documents/{document_id}`
   Return document processing status and chunk count.

4. `POST /query`
   Search indexed chunks, rerank results, generate an answer, cache the response, and record metrics.

5. `GET /metrics/retrieval`
   Return recent retrieval quality and latency records.

Goal: expose the RAG system through HTTP.

## 10. Worker Pipeline

Create:

- `app/workers/pipeline.py`

Build handlers in this order:

1. Handle `document.uploaded`
2. Extract text from the uploaded file
3. Chunk the extracted text
4. Save chunks in PostgreSQL
5. Publish `chunks.created`
6. Generate embeddings
7. Update chunk embeddings in PostgreSQL
8. Publish `embeddings.created`
9. Mark the document as indexed
10. Publish `vector.indexed`

Goal: move heavy document processing out of the API and into an asynchronous worker.

The worker flow should be:

```text
Kafka event -> text extraction -> chunking -> embedding -> vector indexing -> status update
```

## 11. Docker

Create:

- `Dockerfile`
- `docker-compose.yml`

Goal: run the entire system together.

Docker Compose should start:

- FastAPI API
- Worker
- PostgreSQL with pgvector
- Redis
- Redpanda as the Kafka-compatible broker

After this step, the project should run with:

```powershell
docker compose up --build
```

## 12. Tests

Create:

- `tests/test_chunking.py`
- `tests/test_embeddings.py`
- `tests/test_reranker.py`
- `tests/test_llm.py`

Goal: test the small logic-heavy parts first, because they do not require Docker.

Run tests with:

```powershell
python -m pytest
```

## Final Learning Checklist

By the end, you should be able to explain:

- How FastAPI receives and stores uploaded documents.
- Why Kafka is used for asynchronous document processing.
- How document text becomes chunks.
- How LangChain `Document` objects are split into chunks.
- How chunks become embeddings through LangChain `HuggingFaceEmbeddings`.
- How pgvector performs semantic similarity search.
- Why reranking improves retrieval quality.
- How a cross-encoder reranker compares the full question and full chunk together.
- How retrieved context is turned into an answer.
- How Redis caching reduces repeated query latency.
- What metrics are tracked for monitoring retrieval quality and performance.
