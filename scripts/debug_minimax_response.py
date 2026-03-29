from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from openai import OpenAI

from app.core.config import get_settings
from app.core.prompts import ANALYSIS_SYSTEM_PROMPT


def main() -> None:
    settings = get_settings()
    if len(sys.argv) < 2:
        raise SystemExit("用法: python scripts/debug_minimax_response.py '你的问题'")

    question = sys.argv[1]
    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        http_client=httpx.Client(timeout=120.0, trust_env=False),
    )

    messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""用户问题：
{question}

请严格返回 JSON。""",
        },
    ]

    response = client.chat.completions.create(
        model=settings.llm_chat_model,
        messages=messages,
        temperature=0.6,
        extra_body={"reasoning_split": True},
    )

    message = response.choices[0].message
    payload = {
        "model": response.model,
        "content": message.content,
        "reasoning_details": getattr(message, "reasoning_details", None),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
