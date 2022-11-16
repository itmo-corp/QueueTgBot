from marshmallow_dataclass import dataclass
from datetime import datetime
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class JwtToken:
    '''
    token: str
    expires: datetime
    '''
    token: str
    expires: datetime
    Schema: ClassVar[Type[Schema]] = Schema
