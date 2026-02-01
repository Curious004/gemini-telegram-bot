import os
import sys
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai 

# --- 1. FAKE WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! The Bot is running."

def run_http():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- 2. THE DETECTIVE SECTION (DEBUGGING) ---
print("------------------------------------------------")
print("🔍 DIAGNOSTIC MODE: Checking Environment Variables...")

# Get the keys
TELEGRAM_TOKEN = os.environ.get("8475065313:AAHk5TvAsG63Zyaue1h9fnTKmU-b_5yuw4E")
GEMINI_API_KEY = os.environ.get("AIzaSyCcRHAdWeCIxnKZWu4lo-frjcnPpCXhkEo")

# Check Telegram Token
if TELEGRAM_TOKEN:
    print(f"✅ TELEGRAM_TOKEN found! (First 5 chars: {TELEGRAM_TOKEN[:5]}...)")
else:
    print("❌ TELEGRAM_TOKEN is MISSING or NULL")

# Check Gemini Key
if GEMINI_API_KEY:
    print(f"✅ GEMINI_API_KEY found! (First 5 chars: {GEMINI_API_KEY[:5]}...)")
else:
    print("❌ GEMINI_API_KEY is MISSING or NULL")

# Print ALL keys so you can see if you made a typo (like 'TELEGRAM_TOKEN ')
print(f"📋 ALL AVAILABLE KEYS: {list(os.environ.keys())}")
print("------------------------------------------------")

# Stop here if keys are missing so we don't crash with a messy error
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("⚠️ CRITICAL STOP: Please check the 'ALL AVAILABLE KEYS' list above for typos.")
    sys.exit(1) 

# --- 3. NORMAL BOT SETUP ---
client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am connected and running.")

async def chat_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content, model="gemini-2.0-flash", contents=user_text
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("⚠️ Connection Error.")

def main():
    keep_alive()
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_gemini))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
