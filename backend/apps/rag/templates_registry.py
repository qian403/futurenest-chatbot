from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


TEMPLATES_DIR: Path = Path(__file__).resolve().parent.parent.parent / "templates"


@dataclass(frozen=True)
class TemplateMeta:
    template_id: str
    filename: str
    title: str
    description: str = ""


REGISTRY: Dict[str, TemplateMeta] = {
    "labor_standards_act": TemplateMeta(
        template_id="labor_standards_act",
        filename="labor_standards_act.txt",
        title="勞基法",
        description="常見勞動權益規範摘要，供測試 RAG 檢索用。",
    ),
}


def list_templates() -> List[TemplateMeta]:
    return list(REGISTRY.values())


def load_template_text(template_id: str) -> str:
    meta = REGISTRY.get(template_id)
    if not meta:
        raise FileNotFoundError(f"Unknown template_id: {template_id}")
    # 支援 .txt/.md 自動切換，優先使用登記檔名，若不存在則嘗試同名其他副檔名
    primary = TEMPLATES_DIR / meta.filename
    if primary.exists():
        return primary.read_text(encoding="utf-8")
    candidates = []
    # 嘗試交替副檔名
    if primary.suffix.lower() == ".txt":
        candidates.append(primary.with_suffix('.md'))
    elif primary.suffix.lower() == ".md":
        candidates.append(primary.with_suffix('.txt'))
    else:
        candidates.extend([primary.with_suffix('.txt'), primary.with_suffix('.md')])
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    # 找不到任何檔案
    raise FileNotFoundError(f"Template file not found for {template_id}: tried {primary} and {', '.join(map(str, candidates))}")


def extract_article_text(template_id: str, article_no: str) -> str | None:
    """從模板全文中擷取指定條文（例如 "70" -> "第70條 ..." 到下一條或章節為止）。"""
    try:
        text = load_template_text(template_id)
    except Exception:
        return None
    # 正則：從 第{n}條 開始，吃到下一個 "第xx條" 或 "第xx章" 或文件結尾
    pattern = rf"第\s*{re.escape(str(article_no))}\s*條[\s\S]*?(?=\n第\s*\d+\s*條|\n第\s*[一二三四五六七八九十百零〇0-9]+\s*章|\Z)"
    m = re.search(pattern, text)
    return m.group(0) if m else None


_ARTICLE_CACHE: Dict[Tuple[str, str], Optional[str]] = {}


def find_article_any(article_no: str) -> Optional[Tuple[str, str]]:
    """查找所有模板中第 {article_no} 條的全文，回傳 (template_id, text)。"""
    key_hits: List[Tuple[str, str]] = []
    for tid in REGISTRY.keys():
        k = (tid, article_no)
        if k not in _ARTICLE_CACHE:
            _ARTICLE_CACHE[k] = extract_article_text(tid, article_no)
        txt = _ARTICLE_CACHE[k]
        if txt:
            key_hits.append((tid, txt))
    return key_hits[0] if key_hits else None


