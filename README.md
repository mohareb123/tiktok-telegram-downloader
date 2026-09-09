# بوت تنزيل TikTok لـ Telegram

بوت Telegram مكتوب ببايثون يقبل روابط TikTok العامة ويعيد الفيديو بصيغة **MP4** أو منشورات الصور بصيغة **PNG**. يعتمد التنزيل على `yt-dlp`، وتتم معالجة كل طلب في مجلد مؤقت مع حد للحجم ومعدل للطلبات.

## المتطلبات

- Python 3.12+ أو Docker
- توكن Telegram من [@BotFather](https://t.me/BotFather)
- FFmpeg عند التشغيل خارج Docker

## التشغيل المحلي

```bash
cp .env.example .env
# عدّل TELEGRAM_BOT_TOKEN داخل .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a
python -m app
```

## التشغيل باستخدام Docker

```bash
cp .env.example .env
# عدّل التوكن
 docker build -t tiktok-telegram-downloader .
 docker run --rm --env-file .env tiktok-telegram-downloader
```

## الاختبارات

```bash
pytest
ruff check .
```

الاختبارات لا تحتاج إلى توكن Telegram أو اتصال TikTok؛ اختبار التنزيل يستخدم محاكاة محلية. لاختبار التشغيل الحقيقي، أرسل إلى البوت رسالة `/start` ثم رابط TikTok عام. يجب توفير التوكن محليًا فقط وعدم رفع ملف `.env` إلى GitHub.

## الإعدادات

| المتغير | الافتراضي | الغرض |
|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | — | التوكن السري من BotFather |
| `MAX_FILE_SIZE_MB` | `49` | الحد الأقصى للملف قبل الإرسال |
| `DOWNLOAD_TIMEOUT_SECONDS` | `120` | مهلة التنزيل |
| `RATE_LIMIT_SECONDS` | `5` | الفاصل الأدنى بين طلبات المستخدم |
| `LOG_LEVEL` | `INFO` | مستوى السجل |

## ملاحظات الاستخدام

استخدم البوت مع المحتوى الذي تملك حق تنزيله أو إعادة مشاركته، واحترم شروط TikTok وحقوق أصحاب المحتوى. قد لا تعمل الروابط الخاصة أو المحذوفة أو المحمية، وقد يرفض Telegram ملفات تتجاوز حدوده.
