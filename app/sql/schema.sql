create extension if not exists vector;

create table if not exists documents(
    id UUID primary key,
    filename text not null,
    content_type text not null,
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

