# bot.py
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

import database
import admin_handlers
import student_handlers
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        "Error")
# نگهداری وضعیت موقتی برای مدیران (ساده)
user_state = {}

# --- Handlers ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً کد دانشجویی خود را ارسال کنید یا /admin برای ورود مدیر.")


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای ورود به پنل مدیر رمز را ارسال کنید.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # use effective_chat.id which is safer
    chat_id = update.effective_chat.id

    # اگر در حالت admin قرار دارد و رمز صحیح فرستاده
    if text == ADMIN_PASSWORD:
        user_state[chat_id] = {'admin': True}
        await update.message.reply_text(
            "وارد پنل مدیر شدید.\nحالا یک متن چندخطی شامل ثبت نام‌ها بفرست یا فایل اکسل آپلود کن.")
        return

    # اگر مدیر لاگین کرده و متن فرستاد — تبدیل متن به اکسل و افزودن به DB
    st = user_state.get(chat_id, {})
    if st.get('admin'):
        # متن را پارس کن و کاربران را اضافه کن
        # اجرای عملیات دیتابیس و تبدیل اکسل در ترد جداگانه تا لوپ async بلاک نشود
        added = await asyncio.to_thread(admin_handlers.parse_and_add_students_from_text, text)
        if added:
            await update.message.reply_text("دانشجویان اضافه شدند:\n" + "\n".join([f"{c} - {n}" for c, n in added]))
            # همچنین فایل اکسل برگردان (دریافت بایت از thread و بازسازی BytesIO در async)
            excel_bio = await asyncio.to_thread(admin_handlers.text_to_excel_file, text)
            try:
                # some conversions may return a BytesIO already; ensure pointer is at 0
                excel_bio.seek(0)
                await update.message.reply_document(document=excel_bio, filename="classes.xlsx")
            except Exception:
                # fallback: read bytes and send as bytes
                data = excel_bio.getvalue()
                from io import BytesIO
                await update.message.reply_document(document=BytesIO(data), filename="classes.xlsx")
        else:
            await update.message.reply_text("متنی قابل پارس یافت نشد. فرمت هر خط: نام - روز - ساعت شروع تا ساعت پایان - (اختیاری)کد")
        return

    # معمولی: جستجوی دانشجو با کد
    # اجرای کوئری DB در background
    student = await asyncio.to_thread(database.get_student_by_code, text)
    if student:
        # student is a tuple (id, code, name, class_day, start_time, end_time, level)
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

    doc = update.message.document
    f = await doc.get_file()
    b = await f.download_as_bytearray()
    text = admin_handlers.excel_bytes_to_text_wrap(b)
    await update.message.reply_text("تبدیل اکسل به متن:\n\n" + text)


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # ex|simple|STU-...
    parts = data.split('|')
    if parts[0] == 'ex':
        level = parts[1]
        code = parts[2]
        txt = student_handlers.get_sample_exercise(level)
        await query.edit_message_text(txt)
    elif parts[0] == 'status':
        code = parts[1]
        # ساده: پاسخ ثابت (بعدا میشه از جدول progress خوند)
        await query.edit_message_text("وضعیت پیشرفت: هنوز تمرینی ثبت نشده.")


def main():
    database.init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_text))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
