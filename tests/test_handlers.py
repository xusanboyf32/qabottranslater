from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import MAX_FILE_SIZE
from app.handlers import cmd_start, fallback, handle_audio
from app.services.stt import Transcription


def make_message(file_size=1000):
    status = MagicMock()
    status.edit_text = AsyncMock()
    status.delete = AsyncMock()

    message = MagicMock()
    message.voice = SimpleNamespace(file_size=file_size)
    message.audio = None
    message.answer = AsyncMock(return_value=status)
    message.answer_voice = AsyncMock()
    return message, status


def make_bot(audio_bytes=b"audio-bytes"):
    bot = MagicMock()
    bot.download = AsyncMock(return_value=BytesIO(audio_bytes))
    return bot


@pytest.fixture
def services():
    with patch("app.handlers.transcribe", new=AsyncMock()) as stt, \
         patch("app.handlers.translate_to_uzbek", new=AsyncMock()) as translate, \
         patch("app.handlers.synthesize_uzbek", new=AsyncMock()) as tts:
        stt.return_value = Transcription(text="Привет", language="russian")
        translate.return_value = "Salom"
        tts.return_value = b"mp3-bytes"
        yield SimpleNamespace(stt=stt, translate=translate, tts=tts)


async def test_handle_audio_success(services):
    message, status = make_message()
    bot = make_bot()

    await handle_audio(message, bot)

    services.stt.assert_awaited_once_with(b"audio-bytes", "voice.ogg")
    services.translate.assert_awaited_once_with("Привет", "russian")
    services.tts.assert_awaited_once_with("Salom")

    assert message.answer.await_count == 2
    reply_call = message.answer.await_args_list[1]
    assert "Salom" in reply_call.args[0]
    assert reply_call.kwargs["parse_mode"] == "HTML"

    message.answer_voice.assert_awaited_once()
    status.delete.assert_awaited_once()


async def test_uzbek_audio_skips_translation(services):
    services.stt.return_value = Transcription(text="Salom", language="uzbek")
    message, status = make_message()

    await handle_audio(message, make_bot())

    services.translate.assert_not_awaited()
    services.tts.assert_awaited_once_with("Salom")
    message.answer_voice.assert_awaited_once()


async def test_no_speech_found(services):
    services.stt.return_value = Transcription(text="", language="english")
    message, status = make_message()

    await handle_audio(message, make_bot())

    status.edit_text.assert_awaited_once_with("Audioda nutq topilmadi.")
    services.translate.assert_not_awaited()
    services.tts.assert_not_awaited()
    message.answer_voice.assert_not_awaited()


async def test_file_too_large_is_rejected(services):
    message, status = make_message(file_size=MAX_FILE_SIZE + 1)
    bot = make_bot()

    await handle_audio(message, bot)

    message.answer.assert_awaited_once_with("Fayl juda katta (maksimum 20 MB).")
    bot.download.assert_not_awaited()
    services.stt.assert_not_awaited()


@pytest.mark.parametrize("failing_service", ["stt", "translate", "tts"])
async def test_service_error_shows_error_message(services, failing_service):
    getattr(services, failing_service).side_effect = RuntimeError("boom")
    message, status = make_message()

    await handle_audio(message, make_bot())

    status.edit_text.assert_awaited_once_with(
        "❌ Xatolik yuz berdi, keyinroq urinib ko'ring."
    )
    assert message.answer.await_count == 1  # faqat "⏳" xabari, natija yuborilmagan
    message.answer_voice.assert_not_awaited()
    status.delete.assert_not_awaited()


async def test_start_command_greets():
    message = MagicMock()
    message.answer = AsyncMock()

    await cmd_start(message)

    message.answer.assert_awaited_once()
    assert "Salom" in message.answer.await_args.args[0]


async def test_fallback_asks_for_audio():
    message = MagicMock()
    message.answer = AsyncMock()

    await fallback(message)

    message.answer.assert_awaited_once_with(
        "Iltimos, ovozli xabar yoki audio fayl yuboring."
    )


async def test_file_exactly_at_limit_is_accepted(services):
    message, status = make_message(file_size=MAX_FILE_SIZE)

    await handle_audio(message, make_bot())

    services.stt.assert_awaited_once()
    message.answer_voice.assert_awaited_once()


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("meeting.mp3", "meeting.mp3"),
        (None, "audio.mp3"),
    ],
)
async def test_audio_file_name_is_passed_to_stt(services, file_name, expected):
    message, status = make_message()
    message.voice = None
    message.audio = SimpleNamespace(file_size=1000, file_name=file_name)

    await handle_audio(message, make_bot())

    services.stt.assert_awaited_once_with(b"audio-bytes", expected)

