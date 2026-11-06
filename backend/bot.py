import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8916134643"))

bot = Bot(TOKEN)
dp = Dispatcher()


def db():
    con = sqlite3.connect("bot.db")
    con.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(id INTEGER PRIMARY KEY, name TEXT, banned INTEGER DEFAULT 0)"
    )
    return con


def menu(is_admin):
    rows = [
        [InlineKeyboardButton(text="🤖 ربات‌های من", callback_data="bots")],
        [InlineKeyboardButton(text="📁 آپلود فایل", callback_data="upload")],
        [InlineKeyboardButton(text="📊 وضعیت", callback_data="status")],
    ]
    if is_admin:
        rows.append(
            [InlineKeyboardButton(text="👑 پنل مدیریت", callback_data="admin")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(Command("start"))
async def start(m: Message):
    con = db()
    row = con.execute(
        "SELECT banned FROM users WHERE id=?", (m.from_user.id,)
    ).fetchone()
    if row and row[0]:
        con.close()
        return await m.answer("⛔ دسترسی شما مسدود است.")
    con.execute(
        "INSERT OR IGNORE INTO users (id, name) VALUES (?,?)",
        (m.from_user.id, m.from_user.full_name),
    )
    con.commit()
    con.close()
    await m.answer(
        "🦅 ARASH RAVEN HOST\nYOUR BOT, YOUR POWER 🦅",
        reply_markup=menu(m.from_user.id == ADMIN_ID),
    )


@dp.callback_query(F.data == "bots")
async def bots(c: CallbackQuery):
    await c.message.answer("هنوز رباتی نداری. بزودی قابلیت ساخت اضافه میشه.")
    await c.answer()


@dp.callback_query(F.data == "upload")
async def upload(c: CallbackQuery):
    await c.message.answer("آپلود فایل در مرحله‌ی بعد اضافه میشه.")
    await c.answer()


@dp.callback_query(F.data == "status")
async def status(c: CallbackQuery):
    await c.message.answer("✅ سیستم فعال است.")
    await c.answer()


@dp.callback_query(F.data == "admin")
async def admin(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return await c.answer("دسترسی نداری", show_alert=True)
    con = db()
    n = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    con.close()
    await c.message.answer(f"👑 پنل مدیریت\nتعداد کاربران: {n}")
    await c.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
