# RAG Chatbot

基於 Django + React 的檢索增強生成聊天機器人，用於展示 RAG 技術實現。

## 🚀 快速開始

### 技術棧
- **後端**: Django + Django-ninja + SQLite
- **前端**: React + TypeScript + Tailwind CSS  
- **RAG**: LangChain + OpenAI API + ChromaDB

### 環境需求
- Python 3.9+
- Node.js 16+
- OpenAI API Key

### 安裝運行

**後端**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django django-ninja python-dotenv langchain openai chromadb pypdf2
python manage.py migrate
python manage.py runserver
```

**前端**
```bash
cd frontend
npm create react-app . --template typescript
npm install tailwindcss axios
npm start
```

## 📁 專案結構

```
rag-chatbot/
├── backend/          # Django API
├── frontend/         # React UI
├── README.md
└── .gitignore
```

## 📋 開發計劃

### 本週目標

#### ✅ 已完成
- [x] 專案架構規劃

#### 🚧 進行中

**Day 1-2: 後端基礎**
- [ ] Django 專案初始化
- [ ] Django-ninja API 設定
- [ ] SQLite 資料庫設定
- [ ] 基本 API 端點測試 (`/api/health`)

**Day 3-4: RAG 核心**
- [ ] 文件上傳 API (`/api/upload`)
- [ ] 文件解析 (PDF/TXT)
- [ ] ChromaDB 向量儲存設定
- [ ] 基礎問答 API (`/api/chat`)
- [ ] OpenAI API 整合

**Day 5-7: 前端開發**
- [ ] React 專案初始化
- [ ] 聊天介面組件
- [ ] 文件上傳組件
- [ ] API 整合和測試

### MVP 功能清單

**核心功能**
- [ ] 上傳文件 (PDF/TXT)
- [ ] 基於文件內容問答
- [ ] 簡單聊天介面
- [ ] 檔案管理 (列表/刪除)

**技術實現**
- [ ] Django REST API
- [ ] React 聊天 UI
- [ ] SQLite 資料庫
- [ ] ChromaDB 向量儲存
- [ ] OpenAI GPT + Embeddings

## 🔄 開發流程

1. **先讓後端跑起來** - Django + 一個測試 API
2. **實現文件上傳** - 先能上傳和儲存文件
3. **基礎 RAG** - 讀取文件 → 向量化 → 問答
4. **前端介面** - 聊天 UI + 文件上傳
5. **整合測試** - 前後端串接

## 📦 主要依賴

**後端**: `django`, `django-ninja`, `langchain`, `openai`, `chromadb`, `pypdf2`  
**前端**: `react`, `typescript`, `tailwindcss`, `axios`

## 🎯 目標

開發一個能夠上傳文件並基於文件內容進行智能問答的 RAG 系統，作為面試作業展示全端開發和 AI 技術整合能力。

---

**開發原則**: 先做能跑的最小版本，再逐步加功能！  
**目前狀態**: 🚧 準備開始後端開發