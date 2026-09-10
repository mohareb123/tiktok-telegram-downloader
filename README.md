# بوت تنزيل TikTok لـ Telegram

بوت Telegram مكتوب ببايثون يقبل روابط TikTok العامة ويعيد الفيديو بصيغة **MP4**، ومنشورات الصور بصيغة **PNG**، أو الصوت الأصلي بصيغة **MP3**. يستخدم `yt-dlp` مع `curl_cffi` لمحاكاة طلبات Chrome، و`ffmpeg` لمعالجة الوسائط.

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

إذا كانت منصة الاستضافة تشغّل الملف مباشرة، يمكن استخدام:

```bash
python app/bot.py
```

يدعم `app/bot.py` الآن التشغيل المباشر أو الاستيراد كحزمة، لكن يظل `python -m app` هو الأسلوب المفضل.

## الاستخدام داخل Telegram

- أرسل رابط TikTok عاديًا للحصول على MP4 أو PNG تلقائيًا.
- أرسل `/mp3 https://www.tiktok.com/...` لاستخراج الموسيقى أو الصوت الأصلي بصيغة MP3.
- يمكن أيضًا إرسال الرابط متبوعًا بكلمة `mp3`.

يستخدم استخراج MP3 المعالج `FFmpegExtractAudio` بجودة 192 kbps.

## إعدادات مقاومة 403

يستخدم البوت افتراضيًا `TIKTOK_IMPERSONATE=chrome` مع `curl_cffi`، ورؤوس HTTP متناسقة، وإعادة محاولة واحدة بتأخير تدريجي. عند توفر وصول مصرح به إلى المحتوى، يمكن تمرير ملف Cookies بصيغة Netscape:

```env
TIKTOK_IMPERSONATE=chrome
TIKTOK_COOKIE_FILE=/secure/path/tiktok-cookies.txt
```

يجب أن يكون ملف Cookies من جلسة مصرح بها، وأن يبقى خارج المستودع وسجلات التطبيق. لا تستخدم Cookies لحسابات الآخرين، ولا تستخدم Proxy دوّارًا أو وسائل لتجاوز القيود. يجب أن يتم استخراج الرابط وتنزيله من نفس الخادم وIP خلال فترة قصيرة، لأن روابط TikTok قد تكون موقعة وقصيرة العمر.

إذا استمر 403، يعيد البوت رسالة واضحة بدل إعادة المحاولة بلا نهاية. حدّث `yt-dlp` دوريًا عند تغيّر TikTok:

```bash
python -m pip install -U "yt-dlp[default,curl-cffi]"
```

## الاختبارات

```bash
pytest
ruff check .
```

تتضمن الاختبارات محاكاة للتنزيل لاختبار التحويل إلى PNG وMP3 وخيارات المحاكاة دون استهلاك شبكة. لاختبار التنزيل الحقيقي، شغّل البوت وأرسل رابط TikTok عامًا. قد يفشل الاختبار إذا كان الرابط خاصًا أو محذوفًا أو إذا حجب TikTok عنوان IP الخادمي.

## الإعدادات

| المتغير | الافتراضي | الغرض |
|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | — | التوكن السري من BotFather |
| `MAX_FILE_SIZE_MB` | `49` | الحد الأقصى للملف قبل الإرسال |
| `DOWNLOAD_TIMEOUT_SECONDS` | `120` | مهلة التنزيل |
| `RATE_LIMIT_SECONDS` | `5` | الفاصل الأدنى بين طلبات المستخدم |
| `LOG_LEVEL` | `INFO` | مستوى السجل |
| `TIKTOK_IMPERSONATE` | `chrome` | هدف محاكاة المتصفح في curl_cffi |
| `TIKTOK_COOKIE_FILE` | فارغ | مسار اختياري لملف Cookies مصادق عليه |

## ملاحظات الاستخدام

استخدم البوت مع المحتوى الذي تملك حق تنزيله أو إعادة مشاركته، واحترم شروط TikTok وحقوق أصحاب المحتوى. قد يرفض Telegram ملفات تتجاوز حدوده، وقد يرفض TikTok بعض الطلبات حتى مع محاكاة المتصفح.
