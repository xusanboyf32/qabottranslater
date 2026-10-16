from unittest.mock import MagicMock, patch

import pytest

from app.services.tts import synthesize_uzbek


def make_fake_communicate(chunks):
    async def fake_stream():
        for chunk in chunks:
            yield chunk

    communicate = MagicMock()
    communicate.stream = fake_stream
    return communicate


async def test_synthesize_joins_audio_chunks():
    fake = make_fake_communicate(
        [
            {"type": "audio", "data": b"abc"},
            {"type": "audio", "data": b"def"},
        ]
    )

    with patch("app.services.tts.edge_tts.Communicate", return_value=fake):
        result = await synthesize_uzbek("Salom")

    assert result == b"abcdef"


async def test_synthesize_ignores_non_audio_chunks():
    fake = make_fake_communicate(
        [
            {"type": "WordBoundary", "offset": 1, "text": "Salom"},
            {"type": "audio", "data": b"abc"},
        ]
    )

    with patch("app.services.tts.edge_tts.Communicate", return_value=fake):
        result = await synthesize_uzbek("Salom")

    assert result == b"abc"


async def test_synthesize_raises_when_no_audio():
    fake = make_fake_communicate([])

    with patch("app.services.tts.edge_tts.Communicate", return_value=fake):
        with pytest.raises(RuntimeError, match="TTS"):
            await synthesize_uzbek("Salom")

