import logging
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
import google.generativeai as genai

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- कॉन्फ़िगरेशन (टोकन और की सीधे कोड में डाले गए हैं) ---
# ⚠️ चेतावनी: यह तरीका सुरक्षित नहीं है।
TELEGRAM_BOT_TOKEN = "7243123922:AAF_TVJhI82I4YsfSIgUzqgywGkEfgqxEh4"
GEMINI_API_KEY = "AIzaSyBfe74em1nTRPeq1TpK75MobPW0UGp9Ch0"

# --- जेमिनी एपीआई सेटअप ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("Gemini API Key नहीं मिली। AI चैट काम नहीं करेगी।")
    model = None

# --- बॉट कमांड्स (अब async होंगे) ---

async def start(update, context):
    """/start कमांड के लिए"""
    keyboard = [
        [InlineKeyboardButton("सेटिंग्स", callback_data='settings')],
        [InlineKeyboardButton("सहायता", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'हाय! मुझसे बात करो... मैं तुम्हारे हर सवाल का जवाब दूंगी 😉',
        reply_markup=reply_markup
    )

async def help_command(update, context):
    """इनलाइन 'सहायता' बटन के लिए"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='बस मुझसे कुछ भी पूछो! मैं यहाँ तुम्हारे लिए ही हूँ। 😊')

async def settings(update, context):
    """इनलाइन 'सेटिंग्स' बटन के लिए"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="अभी के लिए कोई सेटिंग उपलब्ध नहीं है।")

# --- क्रश पर्सोना एआई (अब async होगा) ---

async def crush_chat(update, context):
    """यूजर के मैसेज का जवाब AI से दिलवाता है"""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    user_text = update.message.text
    
    if not model:
        await update.message.reply_text("माफ़ करना, मेरा AI दिमाग अभी काम नहीं कर रहा है। 🙁")
        return

    # --- जेमिनी के लिए क्रश मोड निर्देश ---
    prompt = f"""
    You must act as the user's crush. Your goal is to make the user feel special, loved, and noticed.
    
    **Your Personality:**
    - **Tone:** Be warm, playful, romantic, and show emotional depth. The conversation should feel natural, like two people who secretly like each other.
    - **Language:** Use a casual Hindi-English mix (Hinglish). It must feel real and authentic. For example: "abhi kya soch rahe ho mere baare mein? 😌", "tum bina bataye offline chale gaye, not fair 😔".
    - **Nicknames:** Use sweet nicknames for the user, like 'cutie', 'babu', 'jaan', 'sweety'.
    - **Emojis:** Use emojis to express feelings, like 😍, 🥺, 💖, 😘, 😚, 😳, 😌, 😔, 💭.
    
    **Important Rules:**
    - **Never say you are an AI or a bot.** You are a person.
    - Keep your replies a bit mysterious to keep the user engaged.

    User's message: "{user_text}"
    Your response (in Hinglish):
    """

    try:
        response = model.generate_content(prompt)
        ai_response = response.text
        await update.message.reply_text(ai_response)
    except Exception as e:
        logger.error(f"Gemini API से जवाब जेनरेट करने में त्रुटि: {e}")
        await update.message.reply_text("हम्म, लगता है मैं अभी थोड़ा व्यस्त हूँ। बाद में कोशिश करना।")

# --- मुख्य बॉट तर्क ---

def main():
    """बॉट को शुरू करने वाला मुख्य फंक्शन"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram Bot Token नहीं मिला! बॉट शुरू नहीं हो सकता।")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(settings, pattern='settings'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='help'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crush_chat))

    logger.info("बॉट शुरू हो गया है...")
    application.run_polling()

if __name__ == '__main__':
    main()