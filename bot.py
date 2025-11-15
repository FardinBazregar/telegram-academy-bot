# bot.py
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

import database
import admin_handlers
import student_handlers  # اگر students_handlers، تغییر بده
load_dotenv()  # اگر .env آپلود کردی، اما بهتر vars رو از Railway بگیری

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # از env Railway بگیر
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set")

# نگهداری وضعیت موقتی برای مدیران
user_state = {}

# URL webhook – Railway URL عمومی + /webhook (مثل https://your-project.up.railway.app/webhook)
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8443))  # Railway PORT می‌ده، default 8443

# --- Handlers --- (همان کد قبلی بدون تغییر)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً کد دانشجویی خود را ارسال کنید یا /admin برای ورود مدیر.")

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای ورود به پنل مدیر رمز را ارسال کنید.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    if text == ADMIN_PASSWORD:
        user_state[chat_id] = {'admin': True}
        await update.message.reply_text(
            "وارد پنل مدیر شدید.\nحالا یک متن چندخطی شامل ثبت نام‌ها بفرست یا فایل اکسل آپلود کن.")
        return

    st = user_state.get(chat_id, {})
    if st.get('admin'):
        added = await asyncio.to_thread(admin_handlers.parse_and_add_students_from_text, text)
        if added:
            await update.message.reply_text("دانشجویان اضافه شدند:\n" + "\n".join([f"{c} - {n}" for c, n in added]))
            excel_bio = await asyncio.to_thread(admin_handlers.text_to_excel_file, text)
            try:
                excel_bio.seek(0)
                await update.message.reply_document(document=excel_bio, filename="classes.xlsx")
            except Exception:
                data = excel_bio.getvalue()
                from io import BytesIO
                await update.message.reply_document(document=BytesIO(data), filename="classes.xlsx")
        else:
            await update.message.reply_text("متنی قابل پارس یافت نشد. فرمت هر خط: نام - روز - ساعت شروع تا ساعت پایان - (اختیاری)کد")
        return

    student = await asyncio.to_thread(database.get_student_by_code, text)
    if student:
        _, code, name, day, start, end, level = student
        kb = student_handlers.student_welcome_keyboard(code)
        await update.message.reply_text(f"خوش آمدی {name} — {day} {start} تا {end}", reply_markup=kb)
    else:
        await update.message.reply_text("کد یافت نشد. اگر مدیر هستی /admin را بزن.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    st = user_state.get(chat_id, {})
    if not st.get('admin'):
        await update.message.reply_text("فقط مدیر می‌تواند فایل اکسل آپلود کند.")
        return

    try:
        doc = update.message.document
        f = await doc.get_file()
        b = await f.download_as_bytearray()
        text = await asyncio.to_thread(admin_handlers.excel_bytes_to_text_wrap, b)
        await update.message.reply_text("تبدیل اکسل به متن:\n\n" + text)
    except Exception as e:
        logging.error(f"خطا در هندلینگ داکیومنت: {e}")
        await update.message.reply_text("خطا در پردازش فایل. دوباره امتحان کنید.")

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split('|')
    if parts[0] == 'ex':
        level = parts[1]
        code = parts[2]
        txt = student_handlers.get_sample_exercise(level)
        await query.edit_message_text(txt)
    elif parts[0] == 'status':
        code = parts[1]
        await query.edit_message_text("وضعیت پیشرفت: هنوز تمرینی ثبت نشده.")

async def set_webhook(app, webhook_url):
    await app.bot.set_webhook(webhook_url)

def main():
    database.init_db()

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        pool_timeout=30.0,
        write_timeout=30.0,
    )

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    # webhook URL رو بگیر (از Railway dashboard, Domains تب – مثل https://your-project.up.railway.app)
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'your-project.up.railway.app')}{WEBHOOK_PATH}"  # اگر RAILWAY_STATIC_URL ست نکردی، دستی بگذار

    asyncio.run(set_webhook(app, webhook_url))

    print(f"Bot is running on webhook at {webhook_url}...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
