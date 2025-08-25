export type ErrorInfo = {
    code: string;
    message: string;
    details?: Record<string, unknown> | null;
};

export type ApiSuccess<T> = {
    success: true;
    data: T;
    error: null;
    trace_id: string;
};

export type ApiFailure = {
    success: false;
    data: null;
    error: ErrorInfo;
    trace_id: string;
};

export type ApiResponse<T> = ApiSuccess<T> | ApiFailure;

export type HealthResponse = {
    status: string;
};

export type ChatSource = {
    id?: string | null;
    document_id?: number | string | null;
    snippet?: string | null;
    score?: number | null;
    article_reference?: string | null;
};

export type ChatTurn = {
    role: 'user' | 'assistant';
    content: string;
};

export type ChatRequest = {
    message: string;
    doc_ids?: number[];
    top_k?: number;
    history?: ChatTurn[];
};

export type ChatResponse = {
    answer: string;
    sources: ChatSource[];
};

// Ingest
export type IngestDocument = {
    doc_id: string;
    text: string;
};

export type IngestRequest = {
    documents: IngestDocument[];
};

export type IngestResult = {
    doc_id: string;
    ok: boolean;
    chunks: number;
    upserts: number;
    error?: string | null;
};

export type IngestResponse = {
    results: IngestResult[];
};

export type TemplateMeta = {
    template_id: string;
    title: string;
    description?: string | null;
};


