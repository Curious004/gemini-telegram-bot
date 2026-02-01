import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- 1. SETUP THE FAKE WEB SERVER (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! The Gemini Bot is running."

def run_http():
    # Render assigns a port via the PORT env variable. Default to 8080 if testing locally.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- 2. CONFIGURE AI & SECRETS ---
# We use os.environ to get keys securely from Render
TELEGRAM_TOKEN = os.environ.get("8475065313:AAHk5TvAsG63Zyaue1h9fnTKmU-b_5yuw4E")
GEMINI_API_KEY = os.environ.get("AIzaSyCcRHAdWeCIxnKZWu4lo-frjcnPpCXhkEo")

# Check if keys are loaded (helpful for debugging)
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing API Keys! Make sure they are set in Render Environment Variables.")

genai.configure(api_key=GEMINI_API_KEY)

# --- 3. BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hello {user_name}! I am connected to Gemini. Ask me anything!")

async def chat_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Show "typing..." status while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # We use a standard model. You can swap this for 'gemini-pro' if 'flash' isn't available.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Run the blocking API call in a separate thread so the bot doesn't freeze
        response = await asyncio.to_thread(model.generate_content, user_text)
        
        # Reply to the user (Markdown support is built-in)
        await update.message.reply_text(response.text)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ I encountered an error connecting to Google Gemini.")

# --- 4. MAIN EXECUTION ---
def main():
    # Start the fake web server first
    keep_alive()
    
    # Start the Telegram bot
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_gemini))
    
    app_bot.run_polling()

if __name__ == '__main__':
    main()