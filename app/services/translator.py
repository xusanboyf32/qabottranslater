from app.config import LLM_MODEL, get_groq_client

SYSTEM_PROMPT = (
    "You are a professional translator. "
    "Translate the user's text into Uzbek (Latin script). "
    "Return ONLY the translation, without any comments or quotes."
)


async def translate_to_uzbek(text: str, source_language: str) -> str:
    client = get_groq_client()
    response = await client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Source language: {source_language}\n\nText:\n{text}",
            },
        ],
    )
    return (response.choices[0].message.content or "").strip()
    #return (response.choices[0].message.content or "")
