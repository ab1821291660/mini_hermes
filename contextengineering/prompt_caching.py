"""
Prompt Caching (Chapter 6)

system_and_3 strategy: cache the system prompt + last 3 non-system messages.
Anthropic allows max 4 cache_control breakpoints.

Only call apply_prompt_caching when the API is Anthropic (Messages API or
compatible gateway). The Agent gates injection via configure_caching() +
_should_apply_prompt_caching(); do not enable on DeepSeek/LM Studio — string
content is converted to content blocks and may break non-Anthropic validators.
"""

import copy
from typing import Any


def apply_prompt_caching(messages: list[dict[str, Any]],
                         cache_ttl: str = "5m") -> list[dict[str, Any]]:
    """Apply system_and_3 caching: system prompt + last 3 messages.

    Returns a deep copy with cache_control breakpoints injected.
    Caller must ensure the target API is Anthropic; otherwise requests may fail.
    """
    messages = copy.deepcopy(messages)
    if not messages:
        return messages


    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"


    breakpoints_used = 0
    # 1. Cache the system prompt (stable across all turns)
    if messages[0].get("role") == "system":
        _mark_message(messages[0], marker)##===================================
        breakpoints_used += 1


    # 2-4. Cache the last 3 non-system messages (rolling window)
    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages))
               if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        _mark_message(messages[idx], marker)##===================================
    return messages


def _mark_message(msg: dict, marker: dict) -> None:
    """Add cache_control to a message, handling string and list content."""
    content = msg.get("content")
    if isinstance(content, str):
        # Convert to content block format for cache_control
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": marker}
        ]
    elif isinstance(content, list) and content:
        last = content[-1]
        if isinstance(last, dict):
            last["cache_control"] = marker
    else:
        msg["cache_control"] = marker
