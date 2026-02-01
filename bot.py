import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai 

# --- 1. KEEP-ALIVE SERVER (Satisfies Render) ---
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

# --- 2. SETUP ---
# We use a default value for local testing, but rely on os.environ for Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8475065313:AAHk5TvAsG63Zyaue1h9fnTKmU-b_5yuw4E")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA55r-ipIRBa6HM2t0Cs7t6jdnft9APG9k")

# Initialize Client safely
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini: {e}")

# --- 3. BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am online and connected to Gemini AI.")

async def chat_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client:
        await update.message.reply_text("⚠️ System Error: AI Key is missing.")
        return

    user_text = update.message.text
    # Typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Generate answer using the new Google GenAI library
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-1.5-flash-001", 
            contents=user_text
        )
        await update.message.reply_text(response.text)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("I'm having trouble connecting to the AI right now.")

# --- 4. START ---
def main():
    keep_alive()
    
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_TOKEN is missing from Environment Variables.")
        # We don't exit here, so the web server stays alive to show logs
    else:
        print("✅ Bot is starting...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_gemini))
        app_bot.run_polling()

if __name__ == '__main__':
    main()



