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
        if "用戶問題:" in prompt:
            try:
                lines = prompt.split('\n')
                user_question = ""
                for line in lines:
                    if line.startswith("用戶問題:"):
                        user_question = line.replace("用戶問題:", "").strip()
                        break
                
                # 檢查是否有相關資料來源
                has_sources = "相關資料來源:" in prompt and "無相關資料" not in prompt
                
                if has_sources:
                    return f"根據提供的資料，關於「{user_question}」的問題，我需要分析相關的勞基法條文來為您提供準確的回答。目前系統正在示範模式中，建議您配置 API 密鑰以獲得完整的 AI 回答功能。"
                else:
                    return f"關於「{user_question}」的問題，我沒有找到直接相關的勞基法資料。這可能需要進一步的法規解釋或諮詢。目前系統正在示範模式中，建議您配置 API 密鑰以獲得完整的 AI 回答功能。"
            except:
                pass
        
        return "系統正在示範模式中運行。請配置 API key環境變數以啟用完整的 AI 功能。"


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
            import google.generativeai as genai 

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            resp = model.generate_content(prompt)
            text = getattr(resp, "text", None) or ""
            return text.strip() or EchoLLM().generate(prompt)
        except Exception as exc:  # pragma: no cover - external SDK
            logger.exception("Google AI generate failed: %s", exc)
            return EchoLLM().generate(prompt)


def get_default_llm() -> BaseLLM:
    """Return Gemini or Echo based on GOOGLE_API_KEY. Simplified provider pipeline."""
    google_key = (os.getenv("GOOGLE_API_KEY") or "").strip()
    gemini_model = (os.getenv("GEMINI_MODEL") or "models/gemini-2.5-flash-lite").strip()
    if google_key:
        return GoogleAiStudioLLM(api_key=google_key, model=gemini_model)
    return EchoLLM()


