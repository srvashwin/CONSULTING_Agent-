import json
import time
from typing import List, Optional
from google import genai
from google.genai import errors
from .config import config


class LLMClient:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            print(
                "\n  ERROR: No GEMINI_API_KEY configured.\n"
                "  Set it in consulting-agent/.env\n"
                "  Get a key at: https://aistudio.google.com/apikey\n"
            )
            exit(1)

        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def _call(self, fn, *args, **kwargs):
        max_retries = 4
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except errors.ServerError as e:
                if attempt < max_retries - 1 and e.code in (429, 500, 502, 503):
                    wait = 2 ** attempt
                    print(f"  Gemini {e.code} (attempt {attempt+1}/{max_retries}), retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise

    def chat_light(self, system: str, messages: List[dict]) -> str:
        return self._call(self._chat, config.GEMINI_MODEL_LIGHT, system, messages, config.MAX_TOKENS_LIGHT)

    def chat_heavy(self, system: str, messages: List[dict]) -> str:
        return self._call(self._chat, config.GEMINI_MODEL_HEAVY, system, messages, config.MAX_TOKENS_HEAVY)

    def _chat(self, model: str, system: str, messages: List[dict], max_tokens: int) -> str:
        contents = self._build_contents(messages)
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config={
                "system_instruction": system,
                "max_output_tokens": max_tokens,
                "temperature": 0.3,
            },
        )
        return response.text

    def structured_light(self, system: str, messages: List[dict], schema: dict) -> dict:
        return self._call(self._structured, config.GEMINI_MODEL_LIGHT, system, messages, schema, config.MAX_TOKENS_LIGHT)

    def structured_heavy(self, system: str, messages: List[dict], schema: dict) -> dict:
        return self._call(self._structured, config.GEMINI_MODEL_HEAVY, system, messages, schema, config.MAX_TOKENS_HEAVY)

    def _structured(
        self, model: str, system: str, messages: List[dict], schema: dict, max_tokens: int
    ) -> dict:
        schema_prompt = (
            f"Return your response as valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n"
            "Return ONLY the JSON. No markdown, no explanation."
        )
        contents = self._build_contents(messages + [{"role": "user", "content": schema_prompt}])
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config={
                "system_instruction": system,
                "max_output_tokens": max_tokens,
                "temperature": 0.2,
            },
        )
        return self._parse_json(response.text)

    def _build_contents(self, messages: List[dict]) -> list:
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ("user", "system") else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })
        return contents

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
