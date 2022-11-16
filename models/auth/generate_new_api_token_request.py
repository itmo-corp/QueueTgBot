from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class GenerateNewAPITokenRequest:
    '''
    userTelegramId: str
    authorityToken: str
    '''
    userTelegramId: str
    authorityToken: str
    Schema: ClassVar[Type[Schema]] = Schema
