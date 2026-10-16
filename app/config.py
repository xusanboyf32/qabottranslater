import os
from functools import lru_cache

from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

STT_MODEL = "whisper-large-v3"
LLM_MODEL = "openai/gpt-oss-120b"
TTS_VOICE = "uz-UZ-MadinaNeural"

MAX_FILE_SIZE = 20 * 1024 * 1024  # Telegram bot yuklab olish limiti: 20 MB


def validate_config() -> None:
    missing = [
        name
        for name, value in (("BOT_TOKEN", BOT_TOKEN), ("GROQ_API_KEY", GROQ_API_KEY))
        if not value
    ]
    if missing:
        raise RuntimeError(f".env faylda yo'q: {', '.join(missing)}")


@lru_cache
def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=GROQ_API_KEY)

