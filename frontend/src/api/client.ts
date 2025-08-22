import type { ApiResponse, HealthResponse, ChatRequest, ChatResponse, ChatTurn, IngestRequest, IngestResponse, TemplateMeta } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
    const res = await fetch(`${API_BASE}${path}`, {
        credentials: 'omit',
        headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
        ...init,
    });
    const json = (await res.json()) as ApiResponse<T>;
    return json;
}

export async function getHealth(): Promise<ApiResponse<HealthResponse>> {
    return request<HealthResponse>('/health');
}

export async function postChat(body: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    return request<ChatResponse>('/chat', { method: 'POST', body: JSON.stringify(body) });
}

// 工具：裁切最近 N 回合（預設 3）並限制每則內容長度（預設 2000 字元）
export function buildChatPayload(
    message: string,
    history: ChatTurn[] = [],
    options: { maxTurns?: number; maxChars?: number } = {}
): ChatRequest {
    const maxTurns = options.maxTurns ?? 3;
    const maxChars = options.maxChars ?? 2000;
    const trim = (s: string) => (s.length > maxChars ? s.slice(-maxChars) : s);
    const trimmedHistory = history.slice(-maxTurns).map((t) => ({ ...t, content: trim(t.content) }));
    return { message: trim(message), history: trimmedHistory };
}

export async function ingestDocuments(body: IngestRequest): Promise<ApiResponse<IngestResponse>> {
    return request<IngestResponse>('/ingest', { method: 'POST', body: JSON.stringify(body) });
}

export async function listTemplates(): Promise<ApiResponse<TemplateMeta[]>> {
    return request<TemplateMeta[]>('/templates');
}

export async function ingestTemplate(template_id: string): Promise<ApiResponse<{ doc_id: string; chunks: number; upserts: number }>> {
    return request('/ingest-template', { method: 'POST', body: JSON.stringify({ template_id }) });
}

