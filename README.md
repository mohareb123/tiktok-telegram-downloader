# بوت تنزيل TikTok لـ Telegram

بوت Telegram مكتوب ببايثون يقبل روابط TikTok العامة ويعيد الفيديو بصيغة **MP4**، ومنشورات الصور بصيغة **PNG**، أو الصوت الأصلي بصيغة **MP3**. يعتمد التنزيل على `yt-dlp` و`ffmpeg`، وتتم معالجة كل طلب في مجلد مؤقت مع حد للحجم ومعدل للطلبات.

## المتطلبات

- Python 3.12+
- FFmpeg مثبت ومتاح في `PATH`
- توكن Telegram من [@BotFather](https://t.me/BotFather)

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

## الاستخدام داخل Telegram

- أرسل رابط TikTok عاديًا للحصول على MP4 أو PNG تلقائيًا.
- أرسل `/mp3 https://www.tiktok.com/...` لاستخراج الموسيقى أو الصوت الأصلي بصيغة MP3.
- يمكن أيضًا إرسال الرابط متبوعًا بكلمة `mp3`.

يستخدم استخراج MP3 المعالج `FFmpegExtractAudio` بجودة 192 kbps. قد لا تعمل الروابط الخاصة أو المحذوفة أو المحمية.

## الاختبارات

```bash
pytest
ruff check .
```

تتضمن الاختبارات محاكاة للتنزيل لاختبار التحويل إلى PNG وMP3 دون استهلاك شبكة. لاختبار التنزيل الحقيقي، شغّل البوت وأرسل إليه رابط TikTok عام، أو نفّذ اختبارًا يدويًا باستخدام `yt-dlp` كما هو موضح أدناه. يجب توفير التوكن محليًا فقط وعدم رفع ملف `.env` إلى GitHub.

### اختبار تنزيل حقيقي من TikTok

```bash
mkdir -p /tmp/tiktok-real-test
.venv/bin/yt-dlp --no-playlist -f bestaudio/best \
  --extract-audio --audio-format mp3 --audio-quality 192K \
  -o '/tmp/tiktok-real-test/%(id)s.%(ext)s' \
  'ضع_رابط_TikTok_عام_هنا'
file /tmp/tiktok-real-test/*
```

قد يفشل هذا الاختبار إذا كان الرابط خاصًا أو محذوفًا أو إذا حجب TikTok الطلب أو تغيرت آلية الوصول لديه.

## الإعدادات

| المتغير | الافتراضي | الغرض |
|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | — | التوكن السري من BotFather |
| `MAX_FILE_SIZE_MB` | `49` | الحد الأقصى للملف قبل الإرسال |
| `DOWNLOAD_TIMEOUT_SECONDS` | `120` | مهلة التنزيل |
| `RATE_LIMIT_SECONDS` | `5` | الفاصل الأدنى بين طلبات المستخدم |
| `LOG_LEVEL` | `INFO` | مستوى السجل |

## ملاحظات الاستخدام

استخدم البوت مع المحتوى الذي تملك حق تنزيله أو إعادة مشاركته، واحترم شروط TikTok وحقوق أصحاب المحتوى. قد يرفض Telegram ملفات تتجاوز حدوده.
