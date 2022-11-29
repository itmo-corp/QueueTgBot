from __future__ import annotations
from enum import Enum
from typing import Generic, TypeVar, Type

T = TypeVar("T")


class OperationResult(Generic[T]):
    def __init__(self, status: OperationStatus, data: T = None) -> None:
        self.status = status
        self.data = data

    @staticmethod
    def from_json(json: dict, type: Type[T] = None) -> OperationResult[T]:
        if (type == None or json["data"] == None):
            return OperationResult(status=OperationStatus(json["status"]))
        if (not hasattr(type, "Schema")):
            if (json["status"] is dict):
                return OperationResult(status=OperationStatus(json["status"]), data=type(**json["data"]))
            return OperationResult(status=OperationStatus(json["status"]), data=type(json["data"]))
        return OperationResult[T](
            status=OperationStatus(json["status"]),
            data=type.Schema().load(json["data"]))


class OperationStatus(Enum):
    Null = 0
    Ok = 1
    Error = 2
    TooManyAttempets = 3
    Wrong = 4
    AlreadyTaken = 5
    NotExists = 6
    Forbid = 7
