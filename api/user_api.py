import requests
from models.queues import *
from models import OperationResult, OperationStatus
from user import User
import configs

BASE_URL = configs.URL + "user/"


def get_name(user: User) -> OperationResult[str]:
    result = user.get(
        BASE_URL + "getDisplayName")
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.result.json(), str)


def set_name(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "setDisplayName", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.result.json())

