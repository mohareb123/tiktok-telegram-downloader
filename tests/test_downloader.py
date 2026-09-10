from pathlib import Path
from unittest.mock import patch

import pytest

from app.downloader import DownloadError, _ydl_options, download_media, is_tiktok_url


@pytest.mark.parametrize(
    "url",
    [
        "https://www.tiktok.com/@user/video/123",
        "https://vm.tiktok.com/ZM123/",
        "https://m.tiktok.com/h5/share/item/123.html",
    ],
)
def test_accepts_tiktok_urls(url):
    assert is_tiktok_url(url)


@pytest.mark.parametrize("url", ["", "https://example.com/video", "javascript://tiktok.com"])
def test_rejects_non_tiktok_urls(url):
    assert not is_tiktok_url(url)


def test_rejects_invalid_url_before_network(tmp_path: Path):
    with pytest.raises(DownloadError, match="ليس رابط TikTok"):
        download_media("https://example.com/x", tmp_path)


def test_converts_image_download_to_png(tmp_path: Path):
    class FakeYDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            from PIL import Image

            output = Path(self.options["outtmpl"].replace("%(id)s.%(ext)s", "abc.jpg"))
            Image.new("RGB", (2, 2), "red").save(output)
            return {"id": "abc", "title": "Test image"}

    with patch("app.downloader.yt_dlp.YoutubeDL", FakeYDL):
        result = download_media("https://www.tiktok.com/@u/photo/1", tmp_path)
    assert result.media_type == "image"
    assert result.path.suffix == ".png"
    assert result.path.exists()


def test_extracts_audio_download_to_mp3(tmp_path: Path):
    class FakeYDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            assert self.options["format"] == "bestaudio/best"
            assert self.options["postprocessors"][0]["preferredcodec"] == "mp3"
            output = Path(self.options["outtmpl"].replace("%(id)s.%(ext)s", "abc.mp3"))
            output.write_bytes(b"fake mp3")
            return {"id": "abc", "title": "Original sound"}

    with patch("app.downloader.yt_dlp.YoutubeDL", FakeYDL):
        result = download_media("https://www.tiktok.com/@u/video/1", tmp_path, media_kind="audio")
    assert result.media_type == "audio"
    assert result.path.suffix == ".mp3"
    assert result.path.read_bytes() == b"fake mp3"


def test_browser_options_include_impersonation_and_cookie_file(tmp_path: Path, monkeypatch):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n")
    monkeypatch.setenv("TIKTOK_IMPERSONATE", "chrome")
    monkeypatch.setenv("TIKTOK_COOKIE_FILE", str(cookie_file))
    options = _ydl_options(tmp_path, 30, "audio")
    assert options["impersonate"] == "chrome"
    assert options["cookiefile"] == str(cookie_file)
    assert options["http_headers"]["User-Agent"].startswith("Mozilla/5.0")
