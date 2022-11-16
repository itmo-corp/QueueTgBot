from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import commands.queues as queues_commands
import commands.manage_queues as manage_queues_commands
import commands.settings as settings_commands
from commands import conversation_keys


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(settings_commands.entry_text),
         KeyboardButton(manage_queues_commands.entry_text)],
        [KeyboardButton(queues_commands.entry_text)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ку", reply_markup=reply_markup)
    return conversation_keys.DEFAULT

queues_commands.parent_handler = start
settings_commands.parent_handler = start
manage_queues_commands.parent_handler = start

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.ALL, start)],
    states={
        conversation_keys.DEFAULT: [
            queues_commands.conv_handler,
            settings_commands.conv_handler,
            manage_queues_commands.conv_handler,
        ],
    },
    fallbacks=[]
)

