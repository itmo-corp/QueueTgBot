from typing import Any
from requests import Response
import requests
import models
import datetime
from models import OperationResult, OperationStatus
from models.auth import UserLoginRequest
from api.auth_api import login as login_to_api


class User:
    def __init__(self, api_token: str, jwt_token: models.auth.JwtToken | None = None) -> None:
        self.api_token = api_token
        self.jwt_token = jwt_token

    def login(self) -> OperationResult:
        if self.jwt_token and self.jwt_token.expires > datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=10):
            return OperationResult(status=OperationStatus.Ok)
        result = login_to_api(UserLoginRequest(apiToken=self.api_token))
        self.jwt_token = result.data
        return OperationResult(status=result.status)

    def post_json(self, url: str, json: Any) -> OperationResult[Response]:
        res = self.login()
        if res.status != OperationStatus.Ok:
            return res
        return OperationResult(status=OperationStatus.Ok, data=requests.post(
            url, json=json, headers={"Authorization": f"Bearer {self.jwt_token.token}"}))

    def get(self, url: str) -> OperationResult[Response]:
        res = self.login()
        if res.status != OperationStatus.Ok:
            return res
        return OperationResult(status=OperationStatus.Ok, data=requests.get(
            url, headers={"Authorization": f"Bearer {self.jwt_token.token}"}))
