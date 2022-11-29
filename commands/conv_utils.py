from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from commands import conversation_keys
from commands.conversation_keys import CONFIRMING, CONFIRM_CALLBACK_FIELD, CONFIRM_NO_CALLBACK_FIELD
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

confirm_kbd_markup = ReplyKeyboardMarkup([
    [KeyboardButton("да"), KeyboardButton("нет")],
], resize_keyboard=True)


def confirm_gen(callback, callback_no=None):
    async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы уверены?", reply_markup=confirm_kbd_markup)
        context.user_data[CONFIRM_CALLBACK_FIELD] = callback
        context.user_data[CONFIRM_NO_CALLBACK_FIELD] = callback_no
        return CONFIRMING

    return confirm


async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "да":
        callback = context.user_data[CONFIRM_CALLBACK_FIELD]
        return await callback(update, context)
    callback_no = context.user_data[CONFIRM_NO_CALLBACK_FIELD]
    if callback_no is not None:
        return await callback_no(update, context)
    return conversation_keys.DEFAULT

confirm_callback_handler = MessageHandler(filters.Regex(r"^да$|^нет$"), confirm_callback)
