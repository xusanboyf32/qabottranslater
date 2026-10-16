from dataclasses import dataclass

from app.config import STT_MODEL, get_groq_client


@dataclass
class Transcription:
    text: str
    language: str  # masalan: "russian", "english", "uzbek"


async def transcribe(audio_bytes: bytes, filename: str) -> Transcription:
    client = get_groq_client()
    response = await client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=STT_MODEL,
        response_format="verbose_json",
    )
    text = (response.text or "").strip()
    language = (getattr(response, "language", None) or "unknown").strip()
    return Transcription(text=text, language=language)
    # return Transcription(text=text, language="unknown")

