from __future__ import annotations

from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator
from apps.common.limits import MESSAGE_MAX_CHARS, HISTORY_ITEM_MAX_CHARS, HISTORY_MAX_TURNS


class HealthResponse(BaseModel):
    status: str = Field(default="ok")


class ChatRequest(BaseModel):
    message: str = Field(..., description="使用者問題或訊息")
    doc_ids: Optional[List[Union[int, str]]] = Field(default=None, description="限制檢索的文件 ID 列表（字串或整數）")
    top_k: int = Field(default=5, ge=1, le=50, description="檢索返回片段數量")
    history: Optional[List["ChatTurn"]] = Field(default=None, description="最近的對話回合，僅保留 N 回合")
    inline_citations: Optional[bool] = Field(default=None, description="是否在回答中加入 [n] 內文引用；預設取環境變數")

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        if len(v) > MESSAGE_MAX_CHARS:
            raise ValueError(f"message too long (>{MESSAGE_MAX_CHARS} chars)")
        return v

    @field_validator("history")
    @classmethod
    def validate_history(cls, v: Optional[List["ChatTurn"]]):
        if v is None:
            return v
        if len(v) > HISTORY_MAX_TURNS:
            raise ValueError(f"history too long (>{HISTORY_MAX_TURNS} turns)")
        return v


class ChatSource(BaseModel):
    id: Optional[str] = None
    document_id: Optional[Union[int, str]] = None
    snippet: Optional[str] = None
    score: Optional[float] = None
    article_reference: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = Field(default_factory=list)
    retrieval: Optional[str] = None


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v: str) -> str:
        if len(v) > HISTORY_ITEM_MAX_CHARS:
            raise ValueError(f"history item too long (>{HISTORY_ITEM_MAX_CHARS} chars)")
        return v


# Ingest schemas
class IngestDocument(BaseModel):
    doc_id: str = Field(..., description="文件的唯一識別 ID")
    text: str = Field(..., description="要索引的純文字內容")


class IngestRequest(BaseModel):
    documents: List[IngestDocument]


class IngestResult(BaseModel):
    doc_id: str
    ok: bool = True
    chunks: int = 0
    upserts: int = 0
    error: Optional[str] = None


class IngestResponse(BaseModel):
    results: List[IngestResult] = Field(default_factory=list)


class TemplateMetaOut(BaseModel):
    template_id: str
    title: str
    description: Optional[str] = None


class IngestTemplateRequest(BaseModel):
    template_id: str


