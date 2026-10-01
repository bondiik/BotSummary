import logging
from logging.handlers import RotatingFileHandler
from telethon import TelegramClient, events
import re
import config
import llm

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),  # консоль
        RotatingFileHandler(
            config.DATA_DIR / "bot.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        ),
    ],
)
log = logging.getLogger("bot")

client = TelegramClient(str(config.SESSION_PATH), config.API_ID, config.API_HASH)

@client.on(events.NewMessage(incoming=True, pattern=r"(?i)^\s*(ping|пинг)\s*$"))
async def pong(event):
    await event.reply("pong")

@client.on(events.ChatAction)
async def on_added_to_chat(event: events.ChatAction.Event):
    if not (event.user_added or event.user_joined):
        return

    me = await client.get_me()
    if me.id not in event.user_ids:
        return

    chat = await event.get_chat()
    title = getattr(chat, "title", None) or str(event.chat_id)
    log.info("Добавлен в чат: %s (id=%s)", title, event.chat_id)

    await event.respond("Привет! Я на месте 👋")

SUMMARY_RE = re.compile(r"(?i)\b(summary|саммари)\b")


@client.on(events.NewMessage(
    incoming=True,
    func=lambda e: e.is_group and e.message.mentioned,
))
async def summary_handler(event: events.NewMessage.Event):
    if not SUMMARY_RE.search(event.raw_text or ""):
        return

    limit = config.NUMBER_RECENT_MESSAGES
    log.info("Запрос саммари: chat=%s, limit=%s", event.chat_id, limit)

    # max_id=event.id исключает саму команду из выборки
    lines = []
    async for m in client.iter_messages(event.chat_id, limit=limit, max_id=event.id):
        if not m.text:
            continue
        sender = m.sender
        name = (
            getattr(sender, "first_name", None)
            or getattr(sender, "title", None)
            or "unknown"
        )
        lines.append(f"[{m.date:%d.%m %H:%M}] {name}: {m.text}")
    lines.reverse()  # от старых к новым

    if not lines:
        await event.reply("Не нашёл текстовых сообщений для саммари.")
        return

    try:
        text = await llm.summarize(lines)
    except Exception:
        log.exception("Ошибка при обращении к OpenRouter")
        await event.reply("Не получилось сделать саммари, попробуйте позже.")
        return

    await event.reply(text[:4000] or "Модель вернула пустой ответ.")

def main():
    client.start(phone=config.PHONE)
    log.info("Бот запущен")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()