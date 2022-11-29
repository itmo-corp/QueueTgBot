from marshmallow_dataclass import dataclass
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class AddMaintainerRequest:
    '''
    queueId: str
    maintainerTelegramId: str
    '''
    queueId: str
    maintainerTelegramId: str
    Schema: ClassVar[Type[Schema]] = Schema
