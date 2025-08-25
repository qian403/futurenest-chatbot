# FutureNest Chatbot

作業內容：部一個有 RAG 的 chatbot，後端框架使用 django+django-ninja，前端使用 react.js。

這是一個小小的面試作業

---

## 專案結構

```
futurenest-chatbot/
├── backend/                      # Django 專案
│   ├── apps/
│   │   ├── api/                  # API 端點 (Django Ninja)
│   │   ├── common/               # 通用：中介層、回應格式、限流等
│   │   └── rag/                  # RAG 能力：向量庫、LLM、ingest 與服務
│   ├── core/                     # Django 設定與路由
│   ├── templates/                # 內建文件範本 (txt)
│   ├── manage.py
│   └── requirements.txt
├── frontend/                     # React + Vite 前端
│   └── src/
│       ├── api/                  # 前端 API client 與型別
│       └── components/           # UI 組件
├── tests/                        # 簡單後端測試
└── README.md
```

---

## 功能

- 健康檢查 `/api/health` 與版本化 API `/api/v1`
- 聊天 `/api/v1/chat`：支援 `history`、`top_k`、`doc_ids`、`inline_citations`
- 文件索引 `/api/v1/ingest`：將任意文本切片後寫入向量庫
- 範本列表 `/api/v1/templates`、匯入範本 `/api/v1/ingest-template`
- RAG：Chroma 持久化，Google Embedding 或本地 Hash 嵌入；檢索與片段去重/排序
- LLM：預設 OpenAI（`OPENAI_API_KEY`），無則回退 Google（`GOOGLE_API_KEY`），再無則 Echo

---

## 需求

- Python 3.9+
- Node.js 16+
- SQLite (內建)
- 選配：OpenAI 或 Google AI Studio API Key

---

## 後端安裝與啟動

```bash
cd backend

# 建虛擬環境
python -m venv .venv

# 虛擬環境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp env.example .env


# 資料庫遷移與啟動
python manage.py migrate
python manage.py runserver
```

後端路由：
- `GET /api/health`（簡易健康檢查，測試用）
- `GET /api/v1/health`（Ninja API 健康）
- `POST /api/v1/chat`
- `POST /api/v1/ingest`
- `GET /api/v1/templates`
- `POST /api/v1/ingest-template`

---

## 前端安裝與啟動

```bash
cd frontend
yarn install  
yarn dev      
```

建立 `frontend/.env`（或 `.env.local`）：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

## 環境變數（backend/.env）

```bash
# 基本
DEBUG=1
SECRET_KEY=dev-secret-not-for-prod
ALLOWED_HOSTS=127.0.0.1,localhost

# CORS
CORS_ALLOW_ALL_ORIGINS=1
# 若上面設為 0，則填入允許來源（逗號分隔）
# CORS_ALLOWED_ORIGINS=http://localhost:5173

# OpenAI（可選）
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Google AI Studio（可選）
GOOGLE_API_KEY=
GEMINI_MODEL=models/gemini-1.5-flash

# RAG
EMBEDDING_MODEL=models/text-embedding-004
VECTOR_DIR=backend/chroma
ANONYMIZED_TELEMETRY=false
SYSTEM_PROMPT=
INLINE_CITATIONS_DEFAULT=1        # 1=啟用回答中的 [n] 內文引用
SNIPPET_MAX_CHARS=300             # 回傳來源片段長度上限

# 其他
# CSRF_TRUSTED_ORIGINS=https://your.domain
```

說明：
- 若 `GOOGLE_API_KEY` 存在，向量嵌入使用 Google Embedding；否則使用本地 Hash 嵌入（可離線）。
- LLM 預設優先使用 OpenAI，無則回退到 Google，兩者都缺則回 Echo 模式（回傳提示的前綴）。

---

## API 說明（/api/v1）

### GET /health
回傳後端狀態（Ninja API）。

回應：
```json
{
  "success": true,
  "data": {"status": "ok"},
  "error": null,
  "trace_id": "..."
}
```

### POST /chat
請求：
```json
{
  "message": "你的問題",
  "history": [{"role": "user", "content": "上一輪"}],
  "top_k": 5,
  "doc_ids": ["labor_standards_act"],
  "inline_citations": false
}
```

回應：
```json
{
  "success": true,
  "data": {
    "answer": "...",
    "sources": [
      {
        "id": "labor_standards_act:article:70",
        "document_id": "labor_standards_act",
        "snippet": "...",
        "article_reference": "勞基法第70條"
      }
    ],
    "retrieval": null
  },
  "error": null,
  "trace_id": "..."
}
```

說明：
- `history` 最多 30 回合，每則最多 4000 字元。
- 當 `inline_citations` 為 `false`（或 `.env` 設 `INLINE_CITATIONS_DEFAULT=0`），系統會移除模型輸出的 `[n]` 樣式。

### POST /ingest
將任意文本切片與嵌入後寫入向量庫。

請求：
```json
{
  "documents": [
    {"doc_id": "custom_doc_1", "text": "要索引的純文字..."}
  ]
}
```

回應：
```json
{
  "success": true,
  "data": {
    "results": [
      {"doc_id": "custom_doc_1", "ok": true, "chunks": 10, "upserts": 10}
    ]
  },
  "error": null,
  "trace_id": "..."
}
```

### GET /templates
取得可用的範本清單。

回應：
```json
{
  "success": true,
  "data": [
    {"template_id": "labor_standards_act", "title": "勞動基準法", "description": "..."}
  ],
  "error": null,
  "trace_id": "..."
}
```

### POST /ingest-template
將指定範本文本匯入向量庫。

請求：
```json
{"template_id": "labor_standards_act"}
```

回應：
```json
{
  "success": true,
  "data": {"doc_id": "labor_standards_act", "chunks": 10, "upserts": 10},
  "error": null,
  "trace_id": "..."
}
```

---

## RAG 流程概覽

1) Ingest：`split_text()` 切片 → 嵌入（Google 或本地）→ 寫入 Chroma collection
2) 檢索：查詢向量 → 取回候選片段 → `_filter_and_rank_contexts()` 過濾/排序與去重
3) 構建提示：`build_prompt()` 將系統提示、來源、對話與問題整合
4) 生成回答：`get_default_llm()` 取得提供者（OpenAI/Google/Echo）→ 後處理（移除 [n] 樣式）

---

## 前端使用重點

- `src/api/client.ts` 已封裝 `getHealth/postChat/ingestDocuments/listTemplates/ingestTemplate`
- `buildChatPayload(message, history, { maxTurns, maxChars })` 會裁切歷史
- 於 `.env` 設定 `VITE_API_BASE_URL` 指向 `/api/v1`

---





