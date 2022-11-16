from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class AddQueueRequest:
    '''
    name: str
    password: str
    '''
    name: str
    password: str
    Schema: ClassVar[Type[Schema]] = Schema
