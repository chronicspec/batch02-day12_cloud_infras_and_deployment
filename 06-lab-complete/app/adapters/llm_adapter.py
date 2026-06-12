from pathlib import Path
import json

import httpx

from app.config import Settings, get_settings
from app.utils.logger import get_logger


class LLMAdapter:
    """OpenAI-compatible adapter with safe fallback to deterministic backend."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.logger = get_logger(__name__)
        self.enabled = bool(
            self.settings.llm_enabled
            and self.settings.llm_api_key
            and self.settings.llm_base_url
        )
        self.provider = self._detect_provider()
        self.prompt_dir = Path(__file__).resolve().parents[1] / "prompts"

    def extract_intent(self, message: str) -> str | None:
        if not self.enabled or not self.settings.llm_intent_model:
            return None
        prompt = self._load_prompt("intent_extractor.txt")
        payload = {
            "model": self.settings.llm_intent_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
        }
        return self._chat_completion(
            payload,
            model=self.settings.llm_intent_model,
            system_prompt=prompt,
            user_content=message,
        )

    def generate_response(self, payload: dict[str, object]) -> str | None:
        if not self.enabled or not self.settings.llm_response_model:
            return None
        prompt = self._load_prompt("response_generator.txt")
        request_payload = {
            "model": self.settings.llm_response_model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }
        return self._chat_completion(
            request_payload,
            model=self.settings.llm_response_model,
            system_prompt=prompt,
            user_content=json.dumps(payload, ensure_ascii=False),
        )

    def _chat_completion(
        self,
        payload: dict[str, object],
        *,
        model: str,
        system_prompt: str,
        user_content: str,
    ) -> str | None:
        if self.provider == "gemini":
            return self._gemini_generate_content(
                model=model,
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=float(payload.get("temperature", 0)),
            )

        return self._openai_chat_completion(payload)

    def _openai_chat_completion(self, payload: dict[str, object]) -> str | None:
        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self.logger.warning(
                "LLM call failed with status %s, fallback to deterministic templates.",
                exc.response.status_code,
            )
            return None
        except httpx.HTTPError:
            self.logger.warning("LLM call failed, fallback to deterministic templates.")
            return None

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return None

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return self._clean_text_response(content)
        return None

    def _gemini_generate_content(
        self,
        *,
        model: str,
        system_prompt: str,
        user_content: str,
        temperature: float,
    ) -> str | None:
        payload = {
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt},
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": user_content},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            },
        }
        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/models/{self._normalize_gemini_model(model)}:generateContent?key={self.settings.llm_api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self.logger.warning(
                "Gemini call failed with status %s, fallback to deterministic templates.",
                exc.response.status_code,
            )
            return None
        except httpx.HTTPError:
            self.logger.warning("Gemini call failed, fallback to deterministic templates.")
            return None

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        content = self._clean_text_response("".join(texts))
        return content or None

    def _load_prompt(self, file_name: str) -> str:
        return (self.prompt_dir / file_name).read_text(encoding="utf-8").strip()

    def _detect_provider(self) -> str:
        provider = (self.settings.llm_provider or "auto").strip().lower()
        if provider != "auto":
            return provider
        if "generativelanguage.googleapis.com" in self.settings.llm_base_url:
            return "gemini"
        return "openai"

    def _normalize_gemini_model(self, model: str) -> str:
        return model.removeprefix("models/")

    def _clean_text_response(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 3:
                cleaned = "\n".join(lines[1:-1]).strip()
        return cleaned
