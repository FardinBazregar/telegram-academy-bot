# راهنمای استقرار بات تلگرام بر روی Railway.app

## گام‌های استقرار (۵ دقیقه)

### 1. آماده‌سازی محلی
```bash
cd c:\Users\FARDIN\Desktop\telegram-academy-bot
# اطمینان از تمام فایل‌های ضروری:
# - Procfile ✓
# - runtime.txt ✓
# - requirements.txt ✓
# - .env (حاوی TELEGRAM_TOKEN)
# - bot.py و سایر فایل‌ها
```

### 2. Git Repository (یک بار)
اگر هنوز Git repo نساختید:
```bash
cd c:\Users\FARDIN\Desktop\telegram-academy-bot
git init
git add .
git commit -m "Initial commit: telegram bot"
```

اگر می‌خواهید در GitHub آپلود کنید (نه اجباری، Railway می‌تواند بدون GitHub هم کار کند):
```bash
# در GitHub یک repo جدید ایجاد کنید (خالی، بدون README)
# سپس:
git remote add origin https://github.com/YOUR_USERNAME/telegram-academy-bot.git
git branch -M main
git push -u origin main
```

### 3. ثبت‌نام و تنظیم Railway

**الف) ورود به Railway:**
1. به https://railway.app بروید
2. کلیک کنید "Login" و سپس GitHub login (یا ایمیل)
3. Dashboard را باز کنید

**ب) New Project:**
1. کلیک "New Project"
2. انتخاب "Deploy from GitHub" (اگر repo را GitHub میں گذاشتید)
   - یا "Empty Project" (اگر فایل‌ها را بدون GitHub آپلود می‌کنید)

**ج) اگر "Empty Project" انتخاب کردید:**
1. پس از ایجاد Project، کلیک "Connect Repo"
2. آپلود فایل‌ها:
   - `zip` فایل پروژه را بسازید
   - آپلود کنید یا با Railway CLI آپلود کنید

**یا ساده‌تر: استفاده از Railway CLI:**
```bash
# نصب Railway CLI (یک بار)
npm install -g @railway/cli
# یا اگر npm ندارید، دانلود از https://railway.app/cli

# ورود
railway login

# استقرار
cd c:\Users\FARDIN\Desktop\telegram-academy-bot
railway init
railway up
```

### 4. تنظیم Environment Variables
در داشبورد Railway:
1. Project خود را باز کنید
2. "Variables" یا "Environment" را کلیک کنید
3. اضافه کنید:
   - `TELEGRAM_TOKEN`: مقدار توکن خود (از `.env`)
   - `ADMIN_PASSWORD`: رمز مدیر (مثلاً `admin123`)

### 5. Deploy
1. Railway خودکار Deploy می‌کند (پس از push یا آپلود)
2. می‌توانید وضعیت را در "Deployments" ببینید
3. انتظار دارید پیام "Bot is running..."

### 6. تست
در تلگرام:
1. بات خود را جستجو کنید
2. `/start` را ارسال کنید
3. بات باید جواب دهد

## مشکل‌حل‌کننده (Troubleshooting)

اگر بات کار نکرد:
1. **Logs را بررسی کنید:**
   - در Railway Dashboard → Project → "Logs"
   - خروجی یا خطاها را ببینید

2. **Environment Variables را چک کنید:**
   - `TELEGRAM_TOKEN` موجود و صحیح است؟

3. **دوباره Deploy کنید:**
   ```bash
   railway up
   # یا در GitHub: push دوباره
   git push
   ```

## اختیاری: استفاده از Replit (هنوز ساده‌تر)

1. به https://replit.com بروید
2. "Create" → "+ Create Repl"
3. "Import from GitHub" (اگر repo دارید) یا "Upload files"
4. `.env` را آپلود کنید یا Environment کنید
5. "Run" را کلیک کنید

Replit خودکار شناخت می‌کند که باید `python bot.py` اجرا شود (اگر `Procfile` موجود است).

---

## خلاصه (ترتیب سریع)

1. ✓ تمام فایل‌های ضروری آماده هستند (`Procfile`, `runtime.txt`, `requirements.txt`)
2. ✓ توکن در `.env` موجود است
3. → Railway.app ثبت‌نام → New Project → Deploy
4. → Environment Variables تنظیم → TELEGRAM_TOKEN و ADMIN_PASSWORD
5. → تست از تلگرام

**اگر هنوز سؤالی دارید، بگویید** و من قدم‌به‌قدم راهنمایی می‌کنم.
