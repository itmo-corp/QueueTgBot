from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class UserLoginRequest:
    '''
    apiToken: str
    '''
    apiToken: str
    Schema: ClassVar[Type[Schema]] = Schema
