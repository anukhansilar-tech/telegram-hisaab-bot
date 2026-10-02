import asyncio
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

import os
import re
from datetime import datetime

from telegram import Bot, Update
from telegram.error import InvalidToken
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters


raw_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TOKEN = "".join(raw_token.split()).strip()
ALLOWED_USER_ID = 8427088619




vinimay_dar = 100.0
fee_percent = 0

# History lists
jama_list = []  # (time, usdt, inr, name)
nikasi_list = []  # (time, inr, usdt, name)


def get_hisaab_text() -> str:
    total_jama_usdt = sum(item[1] for item in jama_list)
    total_jama_inr = sum(item[2] for item in jama_list)
    total_nikasi_inr = sum(item[1] for item in nikasi_list)
    total_nikasi_usdt = sum(item[2] for item in nikasi_list)

    shesh_inr = total_jama_inr - total_nikasi_inr
    shesh_usdt = total_jama_usdt - total_nikasi_usdt

    text = "随意支付\n\n"

    text += f"💹 今日入款 ({len(jama_list)}笔)\n"
    for t, usdt, inr, name in jama_list[-5:]:
        text += f"{t}  +{usdt:.2f}U ({inr:.0f} INR) {name}\n"

    text += "\n"
    text += f"♻️ 今日下发 ({len(nikasi_list)}笔)\n"
    for t, inr, usdt, name in nikasi_list[-5:]:
        text += f"{t}  -{inr:.0f} INR ({usdt:.2f}U) {name}\n"

    text += "\n"
    text += (
        f"总入款 (Total Deposit): {total_jama_inr:.1f} INR "
        f"({total_jama_usdt:.2f}U)\n"
    )
    text += f"汇率 (Rate): {vinimay_dar:.0f}\n"
    text += f"交易费率 (Fee): {fee_percent}%\n\n"
    text += (
        f"已下发 (Total Out): {total_nikasi_inr:.1f} INR | "
        f"{total_nikasi_usdt:.2f}U\n"
    )
    text += (
        f"余额 (Balance): {shesh_inr:.1f} INR | "
        f"{shesh_usdt:.2f}U\n"
    )

    return text


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    global vinimay_dar, jama_list, nikasi_list

            if not update.message or not update.message.text or update.effective_user.id != 8427088619:
            return


    raw_text = update.message.text.strip()
    clean_text = re.sub(r"\[.*?\]\(.*?\)", "", raw_text).strip()
    user_name = (
        update.effective_user.first_name
        if update.effective_user and update.effective_user.first_name
        else "User"
    )
    cur_time = datetime.now().strftime("%H:%M:%S")

    if clean_text.lower().startswith("rate "):
        try:
            vinimay_dar = float(clean_text.split()[1])
            await update.message.reply_text(f"✅ Rate set ho gaya: {vinimay_dar:.0f}")
        except (IndexError, ValueError):
            pass
        return

    if clean_text.lower() in {"reset", "clear"}:
        jama_list.clear()
        nikasi_list.clear()
        await update.message.reply_text("🔄 Hisaab 0 kar diya gaya hai.")
        return

    if clean_text.lower() in {"total", "+total", "hisaab", "hisab"}:
        await update.message.reply_text(get_hisaab_text())
        return

    if clean_text.startswith("+"):
        val_str = (
            clean_text.replace("+", "").replace("U", "").replace("u", "").strip()
        )
        try:
            usdt_val = float(val_str)
            inr_val = usdt_val * vinimay_dar
            jama_list.append((cur_time, usdt_val, inr_val, user_name))
            await update.message.reply_text(get_hisaab_text())
        except ValueError:
            pass
        return

    if clean_text.startswith("-"):
        val_str = (
            clean_text.replace("-", "")
            .replace("INR", "")
            .replace("inr", "")
            .replace("₹", "")
            .strip()
        )
        try:
            inr_val = float(val_str)
            usdt_val = inr_val / vinimay_dar
            nikasi_list.append((cur_time, inr_val, usdt_val, user_name))
            await update.message.reply_text(get_hisaab_text())
        except ValueError:
            pass
        return



async def validate_token() -> None:
    try:
        async with Bot(TOKEN) as bot:
            await bot.get_me()
    except InvalidToken:
        raise SystemExit(
            "Telegram rejected TELEGRAM_BOT_TOKEN. Replace it with the current "
            "token from BotFather."
        ) from None


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
