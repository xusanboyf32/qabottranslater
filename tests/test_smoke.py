import pytest

from app import config
from app.config import get_groq_client
from app.services.translator import translate_to_uzbek

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(not config.GROQ_API_KEY, reason="GROQ_API_KEY yo'q"),
]


@pytest.fixture(autouse=True)
def fresh_client():
    get_groq_client.cache_clear()
    yield
    get_groq_client.cache_clear()


async def test_configured_models_are_available():
    client = get_groq_client()
    models = await client.models.list()
    available = {model.id for model in models.data}

    assert config.STT_MODEL in available
    assert config.LLM_MODEL in available


async def test_real_translation_returns_text():
    result = await translate_to_uzbek("Hello, how are you?", "english")

    assert isinstance(result, str)
    assert result.strip() != ""

