from unittest.mock import AsyncMock, MagicMock, patch

from app.services.translator import translate_to_uzbek

import pytest




def make_fake_client(content):
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


async def test_translate_returns_translation():
    fake_client = make_fake_client("Salom! Ismingiz nima?")

    with patch("app.services.translator.get_groq_client", return_value=fake_client):
        result = await translate_to_uzbek("Привет! Как тебя зовут?", "russian")

    assert result == "Salom! Ismingiz nima?"



async def test_translate_strips_whitespace():
    fake_client = make_fake_client("  \n Salom dunyo \n ")

    with patch("app.services.translator.get_groq_client", return_value=fake_client):
        result = await translate_to_uzbek("Hello world", "english")

    assert result == "Salom dunyo"



async def test_translate_returns_empty_string_when_content_is_none():
    fake_client = make_fake_client(None)

    with patch("app.services.translator.get_groq_client", return_value=fake_client):
        result = await translate_to_uzbek("Hello", "english")

    assert result == ""



async def test_translate_propagates_groq_error():
    client = MagicMock()
    client.chat.completions.create = AsyncMock(side_effect=RuntimeError("groq down"))

    with patch("app.services.translator.get_groq_client", return_value=client):
        with pytest.raises(RuntimeError, match="groq down"):
            await translate_to_uzbek("Hello", "english")

