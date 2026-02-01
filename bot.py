import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai 

# --- 1. FAKE WEB SERVER (Keep-Alive) ---
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

# --- 2. SETUP CLIENTS ---
TELEGRAM_TOKEN = os.environ.get("8475065313:AAHk5TvAsG63Zyaue1h9fnTKmU-b_5yuw4E")
GEMINI_API_KEY = os.environ.get("AIzaSyCcRHAdWeCIxnKZWu4lo-frjcnPpCXhkEo")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    # This explains the error in the logs if keys are missing
    raise ValueError("Missing API Keys! Go to Render -> Environment and add TELEGRAM_TOKEN and GEMINI_API_KEY.")

# New Google GenAI Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

# --- 3. BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm updated and ready. Ask me anything!")

async def chat_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # The new way to call the model using the 'google-genai' library
        # We run it in a thread to keep the bot responsive
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash",  # Using the latest fast model
            contents=user_text
        )
        
        await update.message.reply_text(response.text)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ I had a connection error.")

# --- 4. MAIN LOOP ---
def main():
    keep_alive()
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_gemini))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
