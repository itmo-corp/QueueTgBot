from models.queues import *
from models import OperationResult, OperationStatus
from user import User
import configs

BASE_URL = configs.URL + "queues/"


def create(user: User, request: CreateQueueRequest) -> OperationResult[str]:
    result = user.post_json(
        BASE_URL + "create", json=CreateQueueRequest.Schema().dump(request))
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), str)


def add(user: User, request: AddQueueRequest) -> OperationResult[str]:
    result = user.post_json(
        BASE_URL + "add", json=AddQueueRequest.Schema().dump(request))
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), str)


def forget(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "forget", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def join(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "join", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def leave(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "leave", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def ready(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "ready", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def unready(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "unready", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def get_known_queues(user: User) -> OperationResult[list[str]]:
    result = user.get(
        BASE_URL + "getKnownQueues")
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), list[str])


def get_known_queues_names(user: User) -> OperationResult[list[str]]:
    result = user.get(
        BASE_URL + "getKnownQueuesNames")
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), list[str])


def get_queue_name(user: User, request: str) -> OperationResult[str]:
    result = user.post_json(
        BASE_URL + "getQueueName", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), str)


def get_queue_info(user: User, request: str) -> OperationResult[LabQueueResponce]:
    result = user.post_json(
        BASE_URL + "getQueueInfo", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), LabQueueResponce)


def get_queue_id_by_name(user: User, request: str) -> OperationResult[str]:
    result = user.post_json(
        BASE_URL + "getQueueIdByName", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), str)


def get_im_in_queue(user: User, request: str) -> OperationResult[bool]:
    result = user.post_json(
        BASE_URL + "getImInQueue", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), bool)


def get_maintained_queues_names(user: User) -> OperationResult[list[str]]:
    result = user.get(
        BASE_URL + "getMaintainedQueuesNames")
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), list[str])


def get_maintained_queues_ids(user: User) -> OperationResult[list[str]]:
    result = user.get(
        BASE_URL + "getMaintainedQueuesIds")
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json(), list[str])


def reset_ready(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "resetReady", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def add_maintainer(user: User, request: AddMaintainerRequest) -> OperationResult:
    result = user.post_json(
        BASE_URL + "addMaintainer", json=AddMaintainerRequest.Schema().dump(request))
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())


def leave_maintainer(user: User, request: str) -> OperationResult:
    result = user.post_json(
        BASE_URL + "leaveMaintainer", json=request)
    if (result.status != OperationStatus.Ok):
        return result
    return OperationResult.from_json(result.data.json())
