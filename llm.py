from openrouter import OpenRouter
import config

SYSTEM_PROMPT = """Ты помощник, который делает краткое саммари переписки в Telegram-чате.
Правила:
- Пиши на языке переписки (обычно русский).
- Выдели главные темы, принятые решения, договорённости и открытые вопросы.
- Если важно, укажи, кто что предложил или решил.
- Не выдумывай факты, используй только то, что есть в переписке.
- Формат: короткий список пунктов, без вступлений и заключений.
- Уложись примерно в 1500 символов."""

_client = OpenRouter(api_key=config.OPEN_ROUTER_KEY)

async def summarize(lines: list[str]) -> str:
    chat_text = "\n".join(lines)

    res = await _client.chat.send_async(
        model=config.OPEN_ROUTER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Переписка:\n\n{chat_text}\n\nСделай саммари."},
        ],
    )
    return (res.choices[0].message.content or "").strip()