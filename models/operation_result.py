from __future__ import annotations
from enum import Enum
from typing import Generic, TypeVar, Type

T = TypeVar("T")


class OperationResult(Generic[T]):
    def __init__(self, status: OperationStatus, result: T = None) -> None:
        self.status = status
        self.result = result

    @staticmethod
    def from_json(json: dict, type: Type[T] = None) -> OperationResult[T]:
        if (type == None or json["result"] == None):
            return OperationResult(status=OperationStatus(json["status"]))
        if (not hasattr(type, "Schema")):
            if (json["status"] is dict):
                return OperationResult(status=OperationStatus(json["status"]), result=type(**json["result"]))
            return OperationResult(status=OperationStatus(json["status"]), result=type(json["result"]))
        return OperationResult[T](
            status=OperationStatus(json["status"]),
            result=type.Schema().load(json["result"]))


class OperationStatus(Enum):
    Null = 0
    Ok = 1
    Error = 2
    TooManyAttempets = 3
    Wrong = 4
    AlreadyTaken = 5
    NotExists = 6
    Forbid = 7
