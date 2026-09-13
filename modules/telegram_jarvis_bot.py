"""
================================================================================
👑 BASIT JARVIS AI — TELEGRAM BOT INTEGRATION
================================================================================
Jarvis ko Telegram par lao! 24/7 mobile se control karo apne PC ko.

Features:
- Full bilingual Roman Urdu + English conversation
- All Jarvis commands via Telegram: screenshot, notes, WhatsApp, reminders
- Authorized user whitelist (only Basit bhai)
- Inline buttons for quick actions
- File downloads & uploads
- Real-time status updates

Setup:
1. @BotFather se new bot banao → token milega
2. TELEGRAM_BOT_TOKEN=<token> in .env
3. TELEGRAM_ALLOWED_CHAT_IDS=<your-chat-id> in .env
4. python modules/telegram_jarvis_bot.py

Get your Chat ID: @userinfobot ko /start bhejo
================================================================================
"""

import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_IDS_RAW = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = [int(x.strip()) for x in ALLOWED_IDS_RAW.split(",") if x.strip().isdigit()]
JARVIS_URL = os.getenv("JARVIS_URL", "http://localhost:8888")

# ── Quick action buttons ───────────────────────────────────────────────────────
QUICK_ACTIONS = [
    [("📸 Screenshot", "screenshot lo"), ("📊 Status", "system status batao")],
    [("📝 Notes", "meri notes dikhao"), ("⏰ Reminders", "reminders dikhao")],
    [("🔊 Arsenal", "/arsenal"), ("🤖 Swarm", "/basitswarm health check")],
]


def _send_to_jarvis(command: str) -> str:
    """Send command to Jarvis server and return response."""
    try:
        resp = requests.post(
            f"{JARVIS_URL}/api/command",
            json={"command": command},
            timeout=15
        )
        data = resp.json()
        return data.get("reply") or data.get("response") or data.get("result") or str(data)[:500]
    except requests.Timeout:
        return "⏱️ Jarvis server busy hai bhai — thodi der baad try karo"
    except requests.ConnectionError:
        return f"❌ Jarvis server se connection nahi ho raha ({JARVIS_URL}) — server chal raha hai?"
    except Exception as e:
        return f"❌ Error: {str(e)[:200]}"


def _build_keyboard():
    """Build Telegram inline keyboard for quick actions."""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        for row in QUICK_ACTIONS:
            keyboard.append([InlineKeyboardButton(label, callback_data=cmd) for label, cmd in row])
        return InlineKeyboardMarkup(keyboard)
    except Exception:
        return None


def _is_authorized(chat_id: int) -> bool:
    """Check if user is authorized to use Jarvis bot."""
    if not ALLOWED_CHAT_IDS:
        # No whitelist configured — warn but allow (for initial setup)
        logger.warning("⚠️  No TELEGRAM_ALLOWED_CHAT_IDS set — allowing all users temporarily!")
        return True
    return chat_id in ALLOWED_CHAT_IDS


def _unauthorized_message():
    return (
        "🔐 Access Denied!\n\n"
        "Aap Basit bhai nahi ho 😄\n"
        "Yeh Jarvis sirf Basit ke liye hai!\n\n"
        "Apna Chat ID: /myid command se check karo\n"
        "Phir owner se whitelist karne kaho."
    )


async def start_command(update, context):
    """Handle /start command."""
    from telegram import Update
    chat_id = update.effective_chat.id
    if not _is_authorized(chat_id):
        await update.message.reply_text(_unauthorized_message())
        return

    keyboard = _build_keyboard()
    welcome = (
        "👑 *Basit Jarvis AI — Telegram Portal*\n\n"
        "Salam bhai! Main aapka personal AI assistant hoon.\n"
        "Mujhe koi bhi kaam bol do — main kar dunga! 🚀\n\n"
        "*Quick Commands:*\n"
        "• `screenshot lo` — Screen capture\n"
        "• `note likho: [text]` — Note save karo\n"
        "• `[name] ko WhatsApp karo: [msg]` — WhatsApp\n"
        "• `5 minute baad [task]` — Reminder set karo\n"
        "• `[file.pdf] ko Word banao` — PDF convert\n"
        "• `/status` — System status\n"
        "• `/help` — Full command list\n\n"
        "_Powered by Jarvis Neural Brain_ ⚡"
    )
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def help_command(update, context):
    """Handle /help command."""
    if not _is_authorized(update.effective_chat.id):
        await update.message.reply_text(_unauthorized_message())
        return

    help_text = (
        "👑 *Jarvis Telegram Commands*\n\n"
        "*💬 Conversation:*\n"
        "• Koi bhi Roman Urdu ya English mein likho\n\n"
        "*📸 Screenshot:*\n"
        "• `screenshot lo`\n\n"
        "*📝 Notes:*\n"
        "• `note likho: [text]`\n"
        "• `meri notes dikhao`\n\n"
        "*📱 WhatsApp:*\n"
        "• `ali ko WhatsApp karo: salam bhai`\n\n"
        "*⏰ Reminders:*\n"
        "• `10 minute baad meeting reminder`\n\n"
        "*🔄 File Convert:*\n"
        "• File send karo + `PDF to Word banao`\n\n"
        "*🖥️ System:*\n"
        "• `/status` — Live system metrics\n"
        "• `Chrome kholo` — App open karo\n"
        "• `Atif Aslam chalao` — Music play\n\n"
        "*🤖 Engines:*\n"
        "• `/basit1 [task]` — Code generate\n"
        "• `/basit2 [topic]` — Deep research\n"
        "• `/basit3` — Security audit\n"
        "• `/arsenal` — AI cluster status"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update, context):
    """Handle /status command — live system metrics."""
    if not _is_authorized(update.effective_chat.id):
        await update.message.reply_text(_unauthorized_message())
        return

    await update.message.reply_text("⏳ System status check kar raha hoon...")
    reply = _send_to_jarvis("system status batao")
    await update.message.reply_text(f"🖥️ *System Status*\n\n{reply}", parse_mode='Markdown')


async def myid_command(update, context):
    """Return user's chat ID for whitelist configuration."""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "unknown"
    await update.message.reply_text(
        f"📋 *Your Telegram Info:*\n\n"
        f"Chat ID: `{chat_id}`\n"
        f"Username: @{username}\n\n"
        f"Owner ko yeh ID do TELEGRAM\\_ALLOWED\\_CHAT\\_IDS mein add karne ke liye.",
        parse_mode='Markdown'
    )


async def handle_message(update, context):
    """Handle all text messages — route to Jarvis brain."""
    if not _is_authorized(update.effective_chat.id):
        await update.message.reply_text(_unauthorized_message())
        return

    text = update.message.text.strip()
    if not text:
        return

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )

    # Send to Jarvis
    reply = _send_to_jarvis(text)

    # Reply with keyboard for quick actions
    keyboard = _build_keyboard()
    await update.message.reply_text(
        reply,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_callback(update, context):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    if not _is_authorized(query.message.chat_id):
        await query.answer("Access denied!")
        return

    await query.answer()  # Acknowledge button press
    command = query.data

    # Show processing message
    await query.message.reply_text(f"⚡ Processing: `{command}`...", parse_mode='Markdown')

    reply = _send_to_jarvis(command)

    keyboard = _build_keyboard()
    await query.message.reply_text(
        reply,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_document(update, context):
    """Handle file uploads — auto PDF conversion etc."""
    if not _is_authorized(update.effective_chat.id):
        await update.message.reply_text(_unauthorized_message())
        return

    document = update.message.document
    file_name = document.file_name or "uploaded_file"
    caption = update.message.caption or ""

    await update.message.reply_text(
        f"📎 File mila: `{file_name}`\n\n"
        f"Downloading...",
        parse_mode='Markdown'
    )

    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        save_path = os.path.join(BASE_DIR, "dropzone", file_name)
        os.makedirs(os.path.join(BASE_DIR, "dropzone"), exist_ok=True)
        await file.download_to_drive(save_path)

        # Auto-convert PDF to Word
        if file_name.lower().endswith('.pdf'):
            reply = _send_to_jarvis(f"convert {save_path} to word")
            await update.message.reply_text(
                f"✅ PDF Dropzone mein drop ho gaya!\n\n"
                f"Auto-conversion shuru: {file_name}\n"
                f"Result: {reply}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"✅ File save ho gayi:\n`{save_path}`\n\n"
                f"Koi conversion chahiye? (PDF to Word, etc.)",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(f"❌ File download error: {str(e)[:200]}")


def run_telegram_bot():
    """Start the Telegram bot."""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env!")
        print("   1. @BotFather se bot banao")
        print("   2. Token .env mein add karo: TELEGRAM_BOT_TOKEN=your-token")
        return

    try:
        from telegram.ext import (
            Application, CommandHandler, MessageHandler,
            CallbackQueryHandler, filters
        )
    except ImportError:
        print("❌ python-telegram-bot not installed!")
        print("   pip install python-telegram-bot>=20.7")
        return

    print(f"🤖 Jarvis Telegram Bot starting...")
    print(f"   Authorized IDs: {ALLOWED_CHAT_IDS or 'ALL (configure TELEGRAM_ALLOWED_CHAT_IDS!)'}")
    print(f"   Jarvis URL: {JARVIS_URL}")

    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("myid", myid_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Jarvis Telegram Bot LIVE! Apne phone par test karo.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        # Re-read after loading
        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        ALLOWED_IDS_RAW = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
        ALLOWED_CHAT_IDS = [int(x.strip()) for x in ALLOWED_IDS_RAW.split(",") if x.strip().isdigit()]
    except ImportError:
        pass

    run_telegram_bot()
