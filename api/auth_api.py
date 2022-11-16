import requests
from models.auth import *
from models import OperationResult
import configs

BASE_URL = configs.URL + "auth/"


def register(request: UserRegisterRequest) -> OperationResult:
    responce = requests.post(
        BASE_URL + "register", json=UserRegisterRequest.Schema().dump(request))
    return OperationResult.from_json(responce.json())


def new_api_token(request: GenerateNewAPITokenRequest) -> OperationResult[str]:
    responce = requests.post(
        BASE_URL + "newApiToken", json=GenerateNewAPITokenRequest.Schema().dump(request))
    return OperationResult.from_json(responce.json(), str)


def delete_api_token(request: DeleteApiTokenRequest) -> OperationResult:
    responce = requests.post(
        BASE_URL + "deleteApiToken", json=DeleteApiTokenRequest.Schema().dump(request))
    return OperationResult.from_json(responce.json())


def login(request: UserLoginRequest) -> OperationResult[JwtToken]:
    responce = requests.post(
        BASE_URL + "login", json=UserLoginRequest.Schema().dump(request))
    return OperationResult.from_json(responce.json(), JwtToken)


def list_api_tokens(request: ListAPITokensRequest) -> OperationResult[list[str]]:
    responce = requests.post(
        BASE_URL + "listApiTokens", json=ListAPITokensRequest.Schema().dump(request))
    return OperationResult.from_json(responce.json(), list[str])
