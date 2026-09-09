from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from PIL import Image

TIKTOK_HOSTS = {"tiktok.com", "www.tiktok.com", "m.tiktok.com", "vm.tiktok.com"}


class DownloadError(Exception):
    """Raised when a media download or conversion fails."""


@dataclass(frozen=True)
class DownloadedMedia:
    path: Path
    media_type: str
    title: str


def is_tiktok_url(value: str) -> bool:
    """Return True only for http(s) URLs hosted by TikTok."""
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme in {"http", "https"} and (
        host in TIKTOK_HOSTS or host.endswith(".tiktok.com")
    )


def _safe_title(value: str) -> str:
    cleaned = re.sub(r"[^\w\- ]+", "", value, flags=re.UNICODE).strip()
    return (cleaned[:80] or "tiktok_media").strip()


def download_media(
    url: str, output_dir: Path, timeout: int = 120, media_kind: str = "auto"
) -> DownloadedMedia:
    """Download a TikTok video/image or extract its original audio as MP3."""
    if not is_tiktok_url(url):
        raise DownloadError("الرابط ليس رابط TikTok صالحًا")
    if media_kind not in {"auto", "audio"}:
        raise DownloadError("نوع الوسائط غير مدعوم")
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix="download-", dir=output_dir))
    try:
        options = {
            "outtmpl": str(work_dir / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": timeout,
            "retries": 2,
        }
        if media_kind == "audio":
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:
            options.update({"merge_output_format": "mp4", "format": "best[ext=mp4]/best"})

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = _safe_title(info.get("title") or info.get("id") or "tiktok_media")

        files = [p for p in work_dir.iterdir() if p.is_file()]
        if not files:
            raise DownloadError("لم يتم العثور على ملف وسائط بعد التنزيل")
        source = max(files, key=lambda p: p.stat().st_size)
        if media_kind == "audio":
            destination = output_dir / f"{title}.mp3"
            shutil.move(str(source), destination)
            return DownloadedMedia(destination, "audio", title)
        if source.suffix.lower() in {".jpg", ".jpeg", ".webp", ".heic"}:
            destination = output_dir / f"{title}.png"
            with Image.open(source) as image:
                image.convert("RGB").save(destination, "PNG")
            return DownloadedMedia(destination, "image", title)
        destination = output_dir / f"{title}.mp4"
        shutil.move(str(source), destination)
        return DownloadedMedia(destination, "video", title)
    except DownloadError:
        raise
    except Exception as exc:
        raise DownloadError("تعذر تنزيل الوسائط من TikTok") from exc
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
