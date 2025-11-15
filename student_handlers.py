# student_handlers.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database


def student_welcome_keyboard(student_code):
    keyboard = [
        [InlineKeyboardButton(
            "📘 تمرین ساده", callback_data=f"ex|simple|{student_code}")],
        [InlineKeyboardButton(
            "📙 تمرین متوسط", callback_data=f"ex|medium|{student_code}")],
        [InlineKeyboardButton(
            "📗 وضعیت پیشرفت", callback_data=f"status|{student_code}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_sample_exercise(level):
    if level == "simple":
        return "تمرین ساده:\nیک تابع بنویس که مجموع لیست اعداد را برگرداند."
    if level == "medium":
        return "تمرین متوسط:\nیک تابع بنویس که فاکتوریل اعداد تا n را محاسبه کند."
    return "تمرین پیشنهادی:\nتمرین را انتخاب کنید."
