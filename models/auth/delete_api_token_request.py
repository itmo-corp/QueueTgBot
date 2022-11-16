from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class DeleteApiTokenRequest:
    '''
    token: str
    userTelegramId: str
    authorityToken: str
    '''
    token: str
    userTelegramId: str
    authorityToken: str
    Schema: ClassVar[Type[Schema]] = Schema
