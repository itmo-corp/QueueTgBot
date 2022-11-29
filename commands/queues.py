from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, User as TelegramUser
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from user import User
import configs
from api import auth_api, queue_api
import models
from models import OperationStatus
import re
from commands import conversation_keys
from utils.users import get_user
from commands.conv_utils import confirm_gen, confirm_callback_handler


# states
(
    SELECTING_QUEUE,
    IN_QUEUE

) = range(100, 102)

# local user fields
(
    SELECTED_QUEUE_FIELD,

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
    res = queue_api.get_known_queues(user)

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
                   for i in range(len(queue.members))))
    )

    keyboard = [
        [KeyboardButton(back_to_entry_btn), KeyboardButton(back_btn), KeyboardButton(refresh_queue_btn)],
        [KeyboardButton(join_queue_btn), KeyboardButton(leave_queue_btn), KeyboardButton(unready_queue_btn),],
        [KeyboardButton(join_queue_owerwrite_btn), KeyboardButton(ready_queue_btn)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return IN_QUEUE


async def join_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]
    res = queue_api.get_im_in_queue(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    if res.data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы уже в очереди")
        return IN_QUEUE

    res = queue_api.join(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы успешно записались в очередь")

    return await list_selected_queue(update, context)


async def join_queue_overwrite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]

    res = queue_api.join(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы успешно перезаписались в очередь")

    return await list_selected_queue(update, context)


async def leave_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]

    res = queue_api.leave(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы успешно покинули в очередь")

    return await list_selected_queue(update, context)


async def ready_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]

    res = queue_api.ready(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы готовы")

    return await list_selected_queue(update, context)


async def unready_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    queue_id = context.user_data[SELECTED_QUEUE_FIELD]

    res = queue_api.unready(user, queue_id)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return IN_QUEUE

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы не готовы")

    return await list_selected_queue(update, context)


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.create(user, models.queues.CreateQueueRequest(
        name=context.args[0], password=context.args[1] if len(context.args) > 1 else None))

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"очередь создана")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.add(user, models.queues.AddQueueRequest(
        name=context.args[0], password=context.args[1] if len(context.args) > 1 else None))

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"очередь добавлена")


async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.forget(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"очередь забыта")


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.join(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"вы добавлены в конец очереди")


async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.leave(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"вы покинули очередь")


async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.ready(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"вы теперь готовы")


async def unready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.unready(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"вы теперь не готовы")


async def get_known_queues(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = get_user(update.message.from_user)

    res = queue_api.get_known_queues(user)

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="ваши очереди:\n{}".format('\n'.join(res.data)))


async def get_queue_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.get_queue_name(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"имя очереди: {res.data}")


async def get_queue_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    user = get_user(update.message.from_user)

    res = queue_api.get_queue_info(user, context.args[0])

    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="очередь {}:\n{}".format(
                                       res.data.name, '\n'.join(f'{i + 1}: {res.data.members[i].displayName} - {"готов" if res.data.members[i].isReady else "не готов"}'
                                                                  for i in range(len(res.data.members)))))


entry_text = "Очереди"
parent_handler = None

back_to_entry_btn = "Выбрать очередь"
back_btn = "В главное меню"
join_queue_btn = "Встать в очередь"
join_queue_owerwrite_btn = "Перезаписаться в очередь"
leave_queue_btn = "Покинуть очередь"
refresh_queue_btn = "Обновить очередь"
ready_queue_btn = "Готов"
unready_queue_btn = "Не готов"

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{entry_text}$"), entry)],
    states={
        SELECTING_QUEUE: [
            MessageHandler(filters.Regex(r"^\d+\. ?.+$"), select_queue),
            MessageHandler(filters.Regex(r"^\d+$"), select_queue_by_num),
        ],
        IN_QUEUE: [
            MessageHandler(filters.Regex(f"^{join_queue_btn}$"), join_queue),
            MessageHandler(filters.Regex(f"^{join_queue_owerwrite_btn}$"), confirm_gen(join_queue_overwrite, list_selected_queue)),
            MessageHandler(filters.Regex(f"^{leave_queue_btn}$"), confirm_gen(leave_queue, list_selected_queue)),
            MessageHandler(filters.Regex(f"^{refresh_queue_btn}$"), list_selected_queue),
            MessageHandler(filters.Regex(f"^{ready_queue_btn}$"), ready_queue),
            MessageHandler(filters.Regex(f"^{unready_queue_btn}$"), unready_queue),
        ],
        conversation_keys.CONFIRMING: [
            confirm_callback_handler
        ]
    },
    fallbacks=[
        MessageHandler(filters.Regex(f"^{back_to_entry_btn}$"), entry),
        MessageHandler(filters.Regex(f"^{back_btn}$"), back),
    ],
    map_to_parent={
        conversation_keys.END: conversation_keys.DEFAULT,
        conversation_keys.RESTART: conversation_keys.DEFAULT,
    }
)
