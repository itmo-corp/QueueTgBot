from telegram import User as TelegramUser
from user import User
import configs
from api import auth_api
import models
from models import OperationStatus, OperationResult
import logging


users: dict[str, User] = dict()


def get_user(user: TelegramUser) -> User:
    if user.id in users and users[user.id].login().data == OperationStatus.Ok:
        return users[user.id]
    tokens_res = get_user_token(user.id)
    if tokens_res.status == OperationStatus.NotExists:
        auth_api.register(models.auth.UserRegisterRequest(telegramId=user.id,
                                                          name=user.first_name,
                                                          authorityToken=configs.AUTHORITY_TOKEN))
        tokens_res = get_user_token(user.id)

    if tokens_res.data:
        users[user.id] = User(tokens_res.data)
        return users[user.id]
    
    logging.error(f"произошла авторизация говна {user.id}")
    return User("")


def get_user_token(user_tg_id: str) -> OperationResult[str]:
    tokens_res = auth_api.list_api_tokens(models.auth.ListAPITokensRequest(
        userTelegramId=user_tg_id, authorityToken=configs.AUTHORITY_TOKEN))
    if tokens_res.data and len(tokens_res.data) > 0:
        return OperationResult(OperationStatus.Ok, tokens_res.data[0])
    token_res = auth_api.new_api_token(models.auth.GenerateNewAPITokenRequest(
        userTelegramId=user_tg_id, authorityToken=configs.AUTHORITY_TOKEN))
    return token_res
