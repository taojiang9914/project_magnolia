"""LLM integration: calls Anthropic API for selection, extraction, compaction."""

import json
import os
import re

from anthropic import Anthropic


def is_llm_available() -> bool:
    return bool(os.environ.get("MAGNOLIA_LLM_API_KEY"))


def get_client() -> Anthropic | None:
    key = os.environ.get("MAGNOLIA_LLM_API_KEY")
    if not key:
        return None
    return Anthropic(api_key=key)


def call_llm(system_prompt: str, user_content: str, max_tokens: int = 2000) -> str | None:
    """Call Claude with system + user messages. Returns text or None."""
    client = get_client()
    if not client:
        return None
    model = os.environ.get("MAGNOLIA_LLM_MODEL", "claude-haiku-4-5-20251001")
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        return resp.content[0].text
    except Exception:
        return None


def call_llm_json(system_prompt: str, user_content: str, max_tokens: int = 2000) -> dict | list | None:
    """Call LLM and parse JSON from response."""
    text = call_llm(system_prompt, user_content, max_tokens)
    if not text:
        return None
    m = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
    if m:
        text = m.group(1)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None
