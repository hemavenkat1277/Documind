create extension if not exists vector;

create table if not exists documents(
    id UUID primary key,
    filename text not null,
    content_type text not null,
    storage_path text not null,
    status text non null default 'uploaded',
    error text,
    metadata JSONB not null default '{}'::jsonb,
    created_at TIMESTAMPTZ not null default now(),
    updated_at TIMESTAMPTZ not null default now()
);

create table if not exists chunks (
    id uuid primary key,
    document_id uuid not null references documents(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    token_count integer not null,
    embedding vector(384),
    created_at timestamptz not null default now(),
    unique (document_id,chunk_index)
);

create index if not exosts idx_chunks_document_id on chunks(documed_id);

create index if not exists idx_chunks_embedding on chunks using hnsw (embedding vector_cosine_ops);

create table if not exists pipeline_events(
    id bigserial primary key,
    document_id uuid not null references documents(id) on delete cascade,
    stage text not null,
    payload jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists retrieval_events (
    id uuid primary key,
    question text not null,
    answer text not null,
    latency_ms integer not null,
    top_score double precision,
    cache_hit boolean not null default false,
    answer_length integer not null,
    created at timestamptz not null default now()
);