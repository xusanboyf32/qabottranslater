import pytest

from app.formatting import MAX_PART_LEN, build_reply, is_uzbek


@pytest.mark.parametrize(
    "language, expected",
    [
        ("uzbek", True),
        ("Uzbek", True),
        ("  uzbek  ", True),
        ("uz", True),
        ("russian", False),
        ("english", False),
        ("unknown", False),
        ("", False),
    ],
)
def test_is_uzbek(language, expected):
    assert is_uzbek(language) is expected


def test_build_reply_contains_all_parts():
    reply = build_reply("russian", "Привет", "Salom")
    assert "Russian" in reply
    assert "Привет" in reply
    assert "Salom" in reply


def test_build_reply_escapes_html():
    reply = build_reply("english", "<b>hi</b>", "a & b")
    assert "<b>hi</b>" not in reply
    assert "&lt;b&gt;hi&lt;/b&gt;" in reply
    assert "a &amp; b" in reply


def test_build_reply_trims_long_text():
    long_text = "a" * (MAX_PART_LEN + 500)
    reply = build_reply("english", long_text, "short")
    assert long_text not in reply
    assert "a" * MAX_PART_LEN + "…" in reply


def test_build_reply_keeps_short_text_intact():
    text = "a" * MAX_PART_LEN
    reply = build_reply("english", text, "short")
    assert text in reply
    assert "…" not in reply

