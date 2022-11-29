from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, User as TelegramUser
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from commands.conv_utils import confirm_gen, confirm_callback_handler
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
    SELECTING_QUEUE,
    IN_QUEUE,
    ADDING_MAINTAINER,

) = range(100, 103)

# local user fields
(
    SELECTED_QUEUE_FIELD,

) = range(100, 101)


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await parent_handler(update, context)
    return conversation_keys.END


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await parent_reset_handler(update, context)
    return conversation_keys.RESTART


async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    res = queue_api.get_maintained_queues_names(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return

    queues_names = res.data

    if len(queues_names) > 32:
        queues_names = queues_names[:32]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="жесть у тебя очередей много, все не покажу")

    text = ("Выберите очередь\n" +
            '\n'.join(f'{i + 1}. {queues_names[i]}'
                      for i in range(len(queues_names)))
            )

    keyboard = [
        [KeyboardButton(back_btn)],
        [KeyboardButton(
            f'{i + 1}. {queues_names[i]}') for i in range(len(queues_names))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return SELECTING_QUEUE


async def select_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    queue_id = res.data

    context.user_data[SELECTED_QUEUE_FIELD] = queue_id

    return await list_selected_queue(update, context)


async def select_queue_by_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    m: re.Match = re.search(r"^(\d+)$", update.message.text)
    if not m:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка")
        return await entry(update, context)
    queue_num = m.group(1)
    res = queue_api.get_maintained_queues_ids(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    queue_id = res.data[int(queue_num) - 1]

    context.user_data[SELECTED_QUEUE_FIELD] = queue_id

    return await list_selected_queue(update, context)


async def list_selected_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    queue_id = context.user_data[SELECTED_QUEUE_FIELD]
    res = queue_api.get_queue_info(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    queue = res.data

    text = (
        f"Вы выбрали очередь {queue.name}:\n" +
        ("очередь пуста" if not queue.members else
         '\n'.join(f'{"✅" if queue.members[i].isReady else "❌"}{i + 1}: {queue.members[i].displayName} - {"готов" if queue.members[i].isReady else "не готов"}'
                   for i in range(len(queue.members)))) +
        "\n\n" +
        "Список модераторов:\n" +
        '\n'.join(queue.maintainers)
    )

    keyboard = [
        [KeyboardButton(back_to_entry_btn), KeyboardButton(restart_btn), KeyboardButton(refresh_queue_btn)],
        [KeyboardButton(add_maintainer_btn), KeyboardButton(leave_maintainer_btn)],
        [KeyboardButton(reset_ready_btn)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return IN_QUEUE


async def reset_ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)

    queue_id = context.user_data[SELECTED_QUEUE_FIELD]
    res = queue_api.reset_ready(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    return await list_selected_queue(update, context)


async def add_maintainer_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите id нового модератора (можно посмотреть в настройках)", reply_markup=cancel_kbd_markup)
    return ADDING_MAINTAINER


async def add_maintainer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    m: re.Match = re.search(r"^(\d+)$", update.message.text)
    if not m:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка")
        return await entry(update, context)
    maintainer_id = m.group(1)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]
    res = queue_api.add_maintainer(user,
        models.queues.AddMaintainerRequest(queue_id, maintainer_id))

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Новый модератор успешно добавлен к очереди")

    return await list_selected_queue(update, context)


async def leave_maintainer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]
    res = queue_api.leave_maintainer(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return await entry(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы успешно покинули модерирование очереди")

    return await entry(update, context)


entry_text = "Админ панель"
parent_handler = None
parent_reset_handler = None

back_to_entry_btn = "Выбрать очередь"
restart_btn = "В главное меню"
back_btn = "Назад"
cancel_btn = "Отмена"
reset_ready_btn = "Сбросить готовность"
add_maintainer_btn = "Добавить модератора"
leave_maintainer_btn = "Отказаться от модерки"
refresh_queue_btn = "Обновить очередь"

cancel_kbd = [[KeyboardButton(cancel_btn)]]
cancel_kbd_markup = ReplyKeyboardMarkup(cancel_kbd, resize_keyboard=True)

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{entry_text}$"), entry)],
    states={
        SELECTING_QUEUE: [
            MessageHandler(filters.Regex(r"^\d+\. ?.+$"), select_queue),
            MessageHandler(filters.Regex(r"^\d+$"), select_queue_by_num),
        ],
        IN_QUEUE: [
            MessageHandler(filters.Regex(f"^{refresh_queue_btn}$"), list_selected_queue),
            MessageHandler(filters.Regex(f"^{reset_ready_btn}$"), confirm_gen(reset_ready, list_selected_queue)),
            MessageHandler(filters.Regex(f"^{add_maintainer_btn}$"), add_maintainer_entry),
            MessageHandler(filters.Regex(f"^{leave_maintainer_btn}$"), confirm_gen(leave_maintainer, list_selected_queue)),
        ],
        ADDING_MAINTAINER: [
            MessageHandler(filters.Regex(r"^\d+$"), add_maintainer),
            MessageHandler(filters.Regex(f"^{cancel_btn}$"), list_selected_queue),
        ],
        conversation_keys.CONFIRMING: [
            confirm_callback_handler
        ]
    },
    fallbacks=[
        MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
        MessageHandler(filters.Regex(f"^{back_btn}$"), back),
        MessageHandler(filters.Regex(f"^{restart_btn}$"), restart),
    ],
    map_to_parent={
        conversation_keys.END: conversation_keys.DEFAULT,
        conversation_keys.RESTART: conversation_keys.RESTART,
    }
)
