"""
Context Compression (Chapter 14)

Middle-out compression: protect head + tail, summarize middle.
Includes flush_memories() which appends a user-role sentinel before compression to let the agent save important observations.
"""

def flush_memories(agent, messages: list[dict],
                   min_turns: int = 0) -> None:
    """Give the agent one turn to save memories before compression.

    Appends a user-role sentinel (not a system message), makes one API call
    with the memory tool, then strips all flush artifacts from the list.
    """
    if not agent._tool_handlers.get("memory"):
        return
    if agent._user_turn_count < min_turns:
        return
    if len(messages) < 3:
        return


    sentinel = (
        "[System: The session is being compressed. "
        "Save anything worth remembering -- prioritize user preferences, "
        "corrections, and recurring patterns over task-specific details.]"
    )
    sentinel_idx = len(messages)
    messages.append({"role": "user", "content": sentinel,
                     "_flush": True})

    try:
        # One API call with memory tool only
        memory_schema = [
            t for t in agent.tools
            if t.get("function", {}).get("name") == "memory"
        ]
        resp = agent.client.chat.completions.create(
            model=agent.model,
            messages=[m for m in messages if "_flush" not in m or m == messages[-1]],
            #删除所有包含_flush键的非最后一条消息。====过滤掉所有非最后一条且带有 _flush 标记的消息，只保留最后一条（即刚添加的压缩哨兵）的 _flush 标记。
            ##"_flush" not in m：如果消息字典中没有 "_flush" 键，则保留。
            ##m == messages[-1]：如果消息是最后一条（即刚刚添加的压缩哨兵消息），即使它含有 "_flush" 键，也保留。
            tools=memory_schema or None,
            max_tokens=agent.max_tokens,
        )
        msg = resp.choices[0].message
        tool_calls = getattr(msg, 'tool_calls', None)
        if tool_calls:
            for tc in tool_calls:
                if tc.function.name == "memory":##===================================##===================================
                    import json
                    args = json.loads(tc.function.arguments)
                    agent._execute_tool("memory", args)
    except Exception:
        pass

    # Strip all flush artifacts
    while len(messages) > sentinel_idx:
        messages.pop()
