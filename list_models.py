import asyncio

from app.config import get_groq_client


async def main() -> None:
    client = get_groq_client()
    models = await client.models.list()
    for model in sorted(models.data, key=lambda m: m.id):
        print(model.id)


asyncio.run(main())
