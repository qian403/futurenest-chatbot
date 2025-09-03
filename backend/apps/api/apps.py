from django.apps import AppConfig
import os


def _auto_ingest_if_needed() -> None:
    from apps.rag.templates_registry import list_templates, load_template_text
    from apps.rag.ingest import ingest_text
    flag = (os.getenv("AUTO_INGEST_TEMPLATES") or "0").strip() == "1"
    if not flag:
        return
    try:
        metas = list_templates()
        for meta in metas:
            text = load_template_text(meta.template_id)
            ingest_text(meta.template_id, text)
    except Exception:
        
        pass


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'

    def ready(self):  # type: ignore[override]
        _auto_ingest_if_needed()
