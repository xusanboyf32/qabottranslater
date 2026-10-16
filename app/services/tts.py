import edge_tts

from app.config import TTS_VOICE


async def synthesize_uzbek(text: str) -> bytes:
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    if not audio:
        raise RuntimeError("TTS audio qaytarmadi")
    return bytes(audio)

