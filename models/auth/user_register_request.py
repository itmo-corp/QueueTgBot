from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class UserRegisterRequest:
    '''
    telegramId: str
    name: str
    authorityToken: str
    '''
    telegramId: str
    name: str
    authorityToken: str
    Schema: ClassVar[Type[Schema]] = Schema
