from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from api import user_api
from models import OperationStatus
from commands import conversation_keys
from utils.users import get_user


# states
(
    CHANGING_NAME,

) = range(100, 101)


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await parent_handler(update, context)
    return conversation_keys.END


async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    res = user_api.get_name(user)

    user_name = res.data

    if res.status != OperationStatus.Ok:
        user_name = f"ошибка: {res.status.name}"
    
    res = user_api.get_id(user)

    user_id = res.data

    if res.status != OperationStatus.Ok:
        user_id = f"ошибка: {res.status.name}"

    text = ("🛠 Настройки 🛠\n" +
            f"ваш id: {user_id}\n" +
            f"ваше имя сейчас: {user_name}"
            )

    keyboard = [
        [KeyboardButton(back_btn), KeyboardButton(change_name_btn)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return conversation_keys.DEFAULT


async def change_name_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(back_to_entry_btn)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите новое имя", reply_markup=reply_markup)
    return CHANGING_NAME


async def change_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    new_name = update.message.text.replace('\n', ' ')

    if len(new_name) > 64:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"слишком длинное имя")
        return entry(update, context)

    res = user_api.set_name(user, new_name)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Имя изменено")

    return await entry(update, context)


entry_text = "Настройки"
parent_handler = None

back_to_entry_btn = "Отмена"
back_btn = "В главное меню"
change_name_btn = "Изменить имя"

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{entry_text}$"), entry)],
    states={
        conversation_keys.DEFAULT: [
            MessageHandler(filters.Regex(
                f"^{change_name_btn}$"), change_name_entry),
        ],
        CHANGING_NAME: [
            MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
            MessageHandler(filters.ALL, change_name),
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
        MessageHandler(filters.Regex(f"^{back_btn}$"), back),
    ],
    map_to_parent={
        conversation_keys.END: conversation_keys.DEFAULT,
    }
)
