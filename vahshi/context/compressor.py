"""
Context Compressor — Hermes lossy summarization
وقتی کانتکست به سقف نزدیک شد، وسط مکالمه خلاصه میشه، ابتدا و انتها دست‌نخورده می‌مونه
"""
def compress(messages: list[dict], max_tokens: int = 8000, keep_first: int = 2, keep_last: int = 6) -> list[dict]:
    # rough token estimate: 1 token ~ 4 chars persian
    def est(m): return len(m.get("content","")) // 3
    total = sum(est(m) for m in messages)
    if total <= max_tokens:
        return messages
    # keep system + first N + last M, compress middle
    if len(messages) <= keep_first + keep_last + 1:
        return messages
    head = messages[:keep_first+1]  # include system
    tail = messages[-keep_last:]
    middle = messages[keep_first+1:-keep_last]
    # summary
    summary = "خلاصه مکالمه میانی:\n" + "\n".join([f"{m['role']}: {m['content'][:80]}..." for m in middle[:10]])
    compressed = {"role": "system", "content": f"[فشرده‌سازی خودکار]\n{summary}"}
    return head + [compressed] + tail
