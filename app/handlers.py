import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, Message

from app.config import MAX_FILE_SIZE
from app.formatting import build_reply, is_uzbek
from app.services.stt import transcribe
from app.services.translator import translate_to_uzbek
from app.services.tts import synthesize_uzbek

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Salom! Menga ovozli xabar yoki audio yuboring.\n"
        "Men tilini aniqlayman, matnini yozaman, o'zbekchaga tarjima qilaman "
        "va o'zbekcha ovozda o'qib beraman."
    )


@router.message(F.voice | F.audio)
async def handle_audio(message: Message, bot: Bot) -> None:
    media = message.voice or message.audio
    filename = "voice.ogg" if message.voice else (media.file_name or "audio.mp3")

    if media.file_size and media.file_size > MAX_FILE_SIZE:
        await message.answer("Fayl juda katta (maksimum 20 MB).")
        return

    status = await message.answer("⏳ Qayta ishlanmoqda...")

    try:
        buffer = await bot.download(media)
        audio_bytes = buffer.read()

        transcription = await transcribe(audio_bytes, filename)
        if not transcription.text:
            await status.edit_text("Audioda nutq topilmadi.")
            return

        if is_uzbek(transcription.language):
            translation = transcription.text
        else:
            translation = await translate_to_uzbek(
                transcription.text, transcription.language
            )

        speech = await synthesize_uzbek(translation)
    except Exception:
        logger.exception("Audioni qayta ishlashda xatolik")
        await status.edit_text("❌ Xatolik yuz berdi, keyinroq urinib ko'ring.")
        return

    reply = build_reply(transcription.language, transcription.text, translation)
    await message.answer(reply, parse_mode="HTML")
    await message.answer_voice(
        BufferedInputFile(speech, filename="tarjima.mp3"),
    )

    await status.delete()
    logger.info(
        "Audio qayta ishlandi: til=%s, hajm=%s bayt",
        transcription.language,
        media.file_size,
    )

@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Iltimos, ovozli xabar yoki audio fayl yuboring.")

