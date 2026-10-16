import html

MAX_PART_LEN = 1500


def is_uzbek(language: str) -> bool:
    # return language.strip().lower() in {"uzbek", "uz"}
    return language.strip().lower() in {"uzbek"}


def _trim(text: str) -> str:
    if len(text) <= MAX_PART_LEN:
        return text
    return text[:MAX_PART_LEN] + "…"


def build_reply(language: str, original: str, translation: str) -> str:
    lang_title = language.strip().capitalize()
    original_safe = html.escape(_trim(original))
    translation_safe = html.escape(_trim(translation))
    return (
        f"🌐 <b>Til:</b> {html.escape(lang_title)}\n\n"
        f"📝 <b>Asl matn:</b>\n"
        f"<blockquote>{original_safe}</blockquote>\n\n"
        f"🇺🇿 <b>O'zbekcha tarjima:</b>\n"
        f"<pre>{translation_safe}</pre>"
    )
