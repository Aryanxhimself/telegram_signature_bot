import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# We now read these from environment variables for security
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")
SIGNATURE_TEXT = "\n\n--- Sent via my Signature Bot ---"
# --- End Configuration ---

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Handler Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hello! I am your signature bot. Send me any message, photo, video, or file, "
        "and I will add a signature to it and forward it to the designated channel."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages, adds a signature, and forwards them."""
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    signed_text = f"{user_text}{SIGNATURE_TEXT}"
    await context.bot.send_message(chat_id=TARGET_CHANNEL_ID, text=signed_text)
    await update.message.reply_text("Message forwarded with signature!")

async def handle_media_and_others(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all non-text messages, adds a signature where possible, and forwards them."""
    if not update.message:
        return

    caption = update.message.caption or ""
    signed_caption = f"{caption}{SIGNATURE_TEXT}"
    reply_text = "Forwarded with signature!"

    try:
        if update.message.photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHANNEL_ID, photo=update.message.photo[-1].file_id, caption=signed_caption
            )
            reply_text = "Photo forwarded with signature!"
        elif update.message.video:
            await context.bot.send_video(
                chat_id=TARGET_CHANNEL_ID, video=update.message.video.file_id, caption=signed_caption
            )
            reply_text = "Video forwarded with signature!"
        elif update.message.audio:
            await context.bot.send_audio(
                chat_id=TARGET_CHANNEL_ID, audio=update.message.audio.file_id, caption=signed_caption
            )
            reply_text = "Audio forwarded with signature!"
        elif update.message.document:
            await context.bot.send_document(
                chat_id=TARGET_CHANNEL_ID, document=update.message.document.file_id, caption=signed_caption
            )
            reply_text = "Document forwarded with signature!"
        elif update.message.sticker:
            await context.bot.send_sticker(chat_id=TARGET_CHANNEL_ID, sticker=update.message.sticker.file_id)
            await context.bot.send_message(chat_id=TARGET_CHANNEL_ID, text=SIGNATURE_TEXT)
            reply_text = "Sticker forwarded with signature!"
        else:
            await update.message.forward(chat_id=TARGET_CHANNEL_ID)
            await update.message.reply_text("This message type isn't supported for signatures, but I've forwarded it for you.")
            return

        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error(f"Error handling media: {e}")
        await update.message.reply_text("Sorry, there was an error processing your message.")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN or not TARGET_CHANNEL_ID:
        logger.error("FATAL: BOT_TOKEN or TARGET_CHANNEL_ID not found in environment variables!")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(~filters.COMMAND & ~filters.TEXT, handle_media_and_others))
    application.run_polling()


if __name__ == "__main__":
    main()
