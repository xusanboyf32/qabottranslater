import pytest

from app import config


def test_validate_config_passes_when_all_set(monkeypatch):
    monkeypatch.setattr(config, "BOT_TOKEN", "token")
    monkeypatch.setattr(config, "GROQ_API_KEY", "key")

    assert config.validate_config() is None


@pytest.mark.parametrize(
    "bot_token, groq_key, missing_name",
    [
        (None, "key", "BOT_TOKEN"),
        ("token", None, "GROQ_API_KEY"),
        ("", "key", "BOT_TOKEN"),
        (None, None, "GROQ_API_KEY"),
    ],
)
def test_validate_config_raises_when_missing(
    monkeypatch, bot_token, groq_key, missing_name
):
    monkeypatch.setattr(config, "BOT_TOKEN", bot_token)
    monkeypatch.setattr(config, "GROQ_API_KEY", groq_key)

    with pytest.raises(RuntimeError, match=missing_name):
        config.validate_config()
