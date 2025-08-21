from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


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
    path = TEMPLATES_DIR / meta.filename
    return path.read_text(encoding="utf-8")


