from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.stt import Transcription, transcribe





def make_fake_client(**response_fields):
    client = MagicMock()
    client.audio.transcriptions.create = AsyncMock(
        return_value=SimpleNamespace(**response_fields)
    )
    return client




async def test_transcribe_returns_text_and_language():
    fake_client = make_fake_client(text="Привет! Как тебя зовут?", language="russian")

    with patch("app.services.stt.get_groq_client", return_value=fake_client):
        result = await transcribe(b"fake-audio-bytes", "voice.ogg")

    assert result == Transcription(text="Привет! Как тебя зовут?", language="russian")


async def test_transcribe_strips_whitespace():
    fake_client = make_fake_client(text="  \n Hello world \n ", language=" english ")

    with patch("app.services.stt.get_groq_client", return_value=fake_client):
        result = await transcribe(b"fake-audio-bytes", "voice.ogg")

    assert result == Transcription(text="Hello world", language="english")





async def test_transcribe_language_defaults_to_unknown_when_missing():
    fake_client = make_fake_client(text="Hello")  # language maydoni umuman yo'q

    with patch("app.services.stt.get_groq_client", return_value=fake_client):
        result = await transcribe(b"fake-audio-bytes", "voice.ogg")

    assert result == Transcription(text="Hello", language="unknown")



async def test_transcribe_text_none_becomes_empty_string():
    fake_client = make_fake_client(text=None, language="english")

    with patch("app.services.stt.get_groq_client", return_value=fake_client):
        result = await transcribe(b"fake-audio-bytes", "voice.ogg")

    assert result == Transcription(text="", language="english")


