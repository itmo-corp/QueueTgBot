from marshmallow_dataclass import dataclass
from .queue_member_responce import QueueMemberResponce
from typing import ClassVar, Type
from marshmallow import Schema


@dataclass
class LabQueueResponce:
    '''
    name: str
    members: list[QueueMemberResponce]
    maintainers: list[str]
    '''
    name: str
    members: list[QueueMemberResponce]
    maintainers: list[str]
    Schema: ClassVar[Type[Schema]] = Schema
