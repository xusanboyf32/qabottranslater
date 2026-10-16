import pytest

from app.services.tts import synthesize_uzbek

pytestmark = pytest.mark.smoke


async def test_real_tts_returns_audio():
    audio = await synthesize_uzbek("Salom")

    assert isinstance(audio, bytes)
    assert len(audio) > 1000
