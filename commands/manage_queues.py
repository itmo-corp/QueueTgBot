from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from user import User
import configs
from api import auth_api, queue_api
import models
from models import OperationStatus
import re
from commands import conversation_keys
from utils.users import get_user


# states
(
    ADD_QUEUE_ENTERING_NAME,
    ADD_QUEUE_ENTERING_PASSWORD,
    CREATE_QUEUE_ENTERING_NAME,
    CREATE_QUEUE_ENTERING_PASSWORD,
    FORGET_QUEUE_SELECTING,
) = range(100, 105)

# local user fields
(
    REMEMBERED_QUEUE_NAME,

) = range(100, 101)


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await parent_handler(update, context)
    return conversation_keys.END


async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    res = queue_api.get_known_queues_names(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return

    queues_names = res.result

    text = ("Тут вы можете управлять своими очередями")

    keyboard = [
        [KeyboardButton(back_btn), KeyboardButton(forget_queue_btn)],
        [KeyboardButton(add_queue_btn), KeyboardButton(create_queue_btn)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return conversation_keys.DEFAULT


async def create_queue_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите имя новой очереди", reply_markup=cancel_kbd_markup)
    return CREATE_QUEUE_ENTERING_NAME


no_password_words = [
    "нет",
    "no",
]


async def create_queue_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    queue_name = update.message.text

    if '\n' in queue_name:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Слишком много строк, попробуйте ещё")
        return CREATE_QUEUE_ENTERING_NAME

    if len(queue_name) > 64:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Многобукаф, попробуйте ещё\n(до 64 символов)")
        return CREATE_QUEUE_ENTERING_NAME

    context.user_data[REMEMBERED_QUEUE_NAME] = queue_name

    text = (
        f"Введите пароль для очереди (введите \"{no_password_words[0]}\" без кавычек, чтобы создать без пароля)\n" +
        "(осторожно, пароль не шифруется на сервере)"
    )

    keyboard = [
        [KeyboardButton(no_password_words[0]),
         KeyboardButton(back_to_entry_btn)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    return CREATE_QUEUE_ENTERING_PASSWORD


async def create_queue_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_password = update.message.text

    if not queue_password or queue_password in no_password_words:
        queue_password = None

    res = queue_api.create(user, models.queues.AddQueueRequest(
        name=context.user_data[REMEMBERED_QUEUE_NAME],
        password=queue_password
    ))

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Очередь создана")

    return await entry(update, context)


async def add_queue_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите имя очереди", reply_markup=cancel_kbd_markup)
    return ADD_QUEUE_ENTERING_NAME


async def add_queue_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    queue_name = update.message.text
    res = queue_api.add(user, models.queues.AddQueueRequest(
        name=queue_name, password=None))

    if res.status == OperationStatus.Wrong:
        context.user_data[REMEMBERED_QUEUE_NAME] = queue_name
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите пароль", reply_markup=cancel_kbd_markup)
        return ADD_QUEUE_ENTERING_PASSWORD

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Очередь добавлена")

    return await entry(update, context)


async def add_queue_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_password = update.message.text

    res = queue_api.add(user, models.queues.AddQueueRequest(
        name=context.user_data[REMEMBERED_QUEUE_NAME],
        password=queue_password
    ))

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Очередь добавлена")

    return await entry(update, context)


async def forget_queue_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    res = queue_api.get_known_queues_names(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return

    queues_names = res.result

    if len(queues_names) > 32:
        queues_names = queues_names[:32]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="жесть у тебя очередей много, все не покажу")

    text = ("Выберите очередь, чтобы забыть\n" +
            '\n'.join(f'{i + 1}. {queues_names[i]}'
                      for i in range(len(queues_names)))
            )

    keyboard = [
        [KeyboardButton(back_to_entry_btn)],
        [KeyboardButton(
            f'{i + 1}. {queues_names[i]}') for i in range(len(queues_names))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return FORGET_QUEUE_SELECTING


async def forget_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    m: re.Match = re.search(r"^\d+\. ?(.+)$", update.message.text)
    if not m:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка")
        return await entry(update, context)
    queue_name = m.group(1)
    res = queue_api.get_queue_id_by_name(user, queue_name)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    queue_id = res.result

    res = queue_api.forget(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Очередь успешно забыта")

    return await entry(update, context)


async def forget_queue_by_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    m: re.Match = re.search(r"^(\d+)$", update.message.text)
    if not m:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка")
        return await entry(update, context)
    queue_num = m.group(1)
    res = queue_api.get_known_queues(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    queue_id = res.result[int(queue_num) - 1]

    res = queue_api.forget(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Очередь успешно забыта")

    return await entry(update, context)


entry_text = "Управление очередями"
parent_handler = None

back_to_entry_btn = "Отмена"
back_btn = "В главное меню"
add_queue_btn = "Добавить очередь"
create_queue_btn = "Создать очередь"
forget_queue_btn = "Забыть очередь"


cancel_kbd = [[KeyboardButton(back_to_entry_btn)]]
cancel_kbd_markup = ReplyKeyboardMarkup(cancel_kbd, resize_keyboard=True)


conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{entry_text}$"), entry)],
    states={
        conversation_keys.DEFAULT: [
            MessageHandler(filters.Regex(
                f"^{add_queue_btn}$"), add_queue_entry),
            MessageHandler(filters.Regex(
                f"^{create_queue_btn}$"), create_queue_entry),
            MessageHandler(filters.Regex(
                f"^{forget_queue_btn}$"), forget_queue_entry),
        ],
        ADD_QUEUE_ENTERING_NAME: [
            MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
            MessageHandler(filters.ALL, add_queue_name)],
        ADD_QUEUE_ENTERING_PASSWORD: [
            MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
            MessageHandler(filters.ALL, add_queue_password)],
        CREATE_QUEUE_ENTERING_NAME: [
            MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
            MessageHandler(filters.ALL, create_queue_name)],
        CREATE_QUEUE_ENTERING_PASSWORD: [
            MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
            MessageHandler(filters.ALL, create_queue_password)],
        FORGET_QUEUE_SELECTING: [
            MessageHandler(filters.Regex(r"^\d+\. ?.+$"), forget_queue),
            MessageHandler(filters.Regex(r"^\d+$"), forget_queue_by_num),
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
