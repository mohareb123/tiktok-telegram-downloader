from __future__ import annotations

import asyncio
import importlib
import logging
import os
import re
import sys
import time
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:
    from .downloader import DownloadError, download_media, is_tiktok_url
except ImportError:  # Support hosts that launch or relocate this file directly.
    downloader_module = None
    search_roots = [
        Path.cwd(),
        Path.cwd() / "tiktok-telegram-downloader",
        Path(__file__).resolve().parent,
    ]
    search_roots.extend(Path.cwd().parents)
    search_roots.extend(Path(__file__).resolve().parents)
    for root in dict.fromkeys(search_roots):
        if (root / "app" / "downloader.py").is_file():
            sys.path.insert(0, str(root))
            downloader_module = importlib.import_module("app.downloader")
            break
    if downloader_module is None:
        raise ImportError(
            "لم يتم العثور على app/downloader.py؛ شغّل الملف من مجلد المشروع الكامل"
        ) from None
    DownloadError = downloader_module.DownloadError
    download_media = downloader_module.download_media
    is_tiktok_url = downloader_module.is_tiktok_url

LOGGER = logging.getLogger(__name__)
URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _config() -> tuple[str, int, int, float]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    max_mb = int(os.environ.get("MAX_FILE_SIZE_MB", "49"))
    timeout = int(os.environ.get("DOWNLOAD_TIMEOUT_SECONDS", "120"))
    rate = float(os.environ.get("RATE_LIMIT_SECONDS", "5"))
    return token, max_mb, timeout, rate


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "مرحبًا! أرسل رابط TikTok وسأعيد الفيديو MP4 أو الصور PNG.\n"
        "لاستخراج الصوت MP3 استخدم: /mp3 ثم الرابط.\n"
        "استخدم /help للمساعدة."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "أرسل رابط TikTok عام للحصول على MP4 أو PNG.\n"
        "لاستخراج الموسيقى/الصوت الأصلي بصيغة MP3:\n"
        "1. أرسل /mp3 ثم مسافة ثم الرابط\n"
        "2. أو أرسل الرابط متبوعًا بكلمة mp3\n"
        "قد تفشل الروابط الخاصة أو المحمية أو المحذوفة."
    )


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    text = " ".join(context.args).strip()
    await process_url(update, context, text, media_kind="audio")


async def process_url(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, media_kind: str = "auto"
) -> None:
    url_match = URL_RE.search(text)
    if not url_match or not is_tiktok_url(url_match.group(0)):
        await update.message.reply_text("أرسل رابط TikTok صالحًا يبدأ بـ https://www.tiktok.com/")
        return

    _, _, _, rate = _config()
    now = time.monotonic()
    last = context.user_data.get("last_request", 0.0)
    if now - last < rate:
        await update.message.reply_text("تمهل قليلًا ثم أرسل رابطًا آخر.")
        return
    context.user_data["last_request"] = now
    status = await update.message.reply_text("جارٍ التنزيل، يرجى الانتظار...")
    await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    output_dir = Path("/tmp/tiktok-downloader") / str(update.effective_user.id)
    try:
        _, max_mb, timeout, _ = _config()
        media = await asyncio.to_thread(
            download_media, url_match.group(0), output_dir, timeout, media_kind
        )
        if media.path.stat().st_size > max_mb * 1024 * 1024:
            raise DownloadError(f"حجم الملف أكبر من الحد المسموح ({max_mb} MB)")
        with media.path.open("rb") as handle:
            if media.media_type == "video":
                await update.message.reply_video(video=handle, caption=media.title[:1024])
            elif media.media_type == "image":
                await update.message.reply_photo(photo=handle, caption=media.title[:1024])
            else:
                await update.message.reply_audio(audio=handle, title=media.title[:64])
        await status.delete()
    except DownloadError as exc:
        await status.edit_text(str(exc))
    except Exception:
        LOGGER.exception("Unexpected request failure")
        await status.edit_text("حدث خطأ غير متوقع. حاول لاحقًا.")
    finally:
        if output_dir.exists():
            for child in output_dir.iterdir():
                child.unlink(missing_ok=True)
            output_dir.rmdir()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    media_kind = "audio" if re.search(r"(?:^|\s)mp3(?:\s|$)", text, re.IGNORECASE) else "auto"
    await process_url(update, context, text, media_kind)


def build_application(token: str) -> Application:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mp3", audio_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return application


def main() -> None:
    token, _, _, _ = _config()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    build_application(token).run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
