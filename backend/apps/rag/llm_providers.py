from __future__ import annotations

import logging
import os
from typing import Optional


logger = logging.getLogger(__name__)


class BaseLLM:
    def generate(self, prompt: str) -> str: 
        raise NotImplementedError


class EchoLLM(BaseLLM):
    def generate(self, prompt: str) -> str:
        return f"[demo] {prompt[:800]}"


class GoogleAiStudioLLM(BaseLLM):
    def __init__(self, api_key: Optional[str], model: str = "models/gemini-1.5-flash") -> None:
        self.api_key = api_key
        if model.startswith("models/") or model.startswith("tunedModels/"):
            self.model = model
        else:
            self.model = f"models/{model}"

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("Google API key missing, fallback to echo")
            return EchoLLM().generate(prompt)
        try:
            # Lazy import to avoid hard dependency if not used
            import google.generativeai as genai 

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            resp = model.generate_content(prompt)
            text = getattr(resp, "text", None) or ""
            return text.strip() or EchoLLM().generate(prompt)
        except Exception as exc:  # pragma: no cover - external SDK
            logger.exception("Google AI generate failed: %s", exc)
            return EchoLLM().generate(prompt)


class OpenAiLLM(BaseLLM):
    def __init__(self, api_key: Optional[str], model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("OpenAI API key missing, fallback to echo")
            return EchoLLM().generate(prompt)
        try:
            # Lazy import to avoid hard dependency if not used
            import openai  # type: ignore

            client = openai.OpenAI(api_key=self.api_key)  # type: ignore[attr-defined]
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = completion.choices[0].message.content or ""
            return content.strip() or EchoLLM().generate(prompt)
        except Exception as exc: 
            logger.exception("OpenAI generate failed: %s", exc)
            return EchoLLM().generate(prompt)


def get_default_llm() -> BaseLLM:
    """Return default LLM provider (OpenAI). Falls back to Google AI Studio if OpenAI key not available."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAiLLM(api_key=openai_key, model=openai_model)
    
    # Fallback to Google AI Studio
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "models/gemma-2-9b-it")
    return GoogleAiStudioLLM(api_key=google_key, model=gemini_model)


