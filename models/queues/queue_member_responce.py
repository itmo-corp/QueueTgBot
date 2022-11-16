from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema

@dataclass
class QueueMemberResponce:
    '''
    displayName: str
    isReady: bool
    '''
    displayName: str
    isReady: bool
    Schema: ClassVar[Type[Schema]] = Schema
