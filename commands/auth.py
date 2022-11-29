from telegram import Update
from telegram.ext import ContextTypes
import configs
from api import auth_api
import models
from models import OperationStatus


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = auth_api.register(models.auth.UserRegisterRequest(telegramId=update.message.from_user.id,
                                                            name=update.message.from_user.first_name,
                                                            authorityToken=configs.AUTHORITY_TOKEN))
    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка регистрации: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="успешная регистрация")


async def new_api_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = auth_api.new_api_token(models.auth.GenerateNewAPITokenRequest(userTelegramId=update.message.from_user.id,
                                                                        authorityToken=configs.AUTHORITY_TOKEN))
    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"новый токен: {res.data}")


async def list_api_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = auth_api.list_api_tokens(models.auth.ListAPITokensRequest(userTelegramId=update.message.from_user.id,
                                                                    authorityToken=configs.AUTHORITY_TOKEN))
    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="ваши токены:\n{}".format('\n'.join(res.data)))


async def delete_api_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (len(context.args) < 1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ожидался 1 аргумент")
        return

    res = auth_api.delete_api_token(models.auth.DeleteApiTokenRequest(token=context.args[0],
                                                                      userTelegramId=update.message.from_user.id,
                                                                      authorityToken=configs.AUTHORITY_TOKEN))
    if res.status != OperationStatus.Ok:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ошибка: {res.status.name}")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"удалено")
