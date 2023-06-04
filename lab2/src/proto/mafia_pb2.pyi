from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

BAD_REQUEST: StatusCode
BROADCAST_MESSAGE: CommunicationDataType
CREATED: StatusCode
DECISION_MESSAGE: CommunicationDataType
DESCRIPTOR: _descriptor.FileDescriptor
EMPTY_MESSAGE: CommunicationDataType
FORBIDDEN: StatusCode
HANDSHAKE_MESSAGE: CommunicationDataType
NOT_FOUND: StatusCode
OK: StatusCode
UNSPECIFIED: StatusCode
VOTE_MESSAGE: CommunicationDataType

class AddUserRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class BaseUserRequest(_message.Message):
    __slots__ = ["user_id"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class CommunicationRequest(_message.Message):
    __slots__ = ["data_type", "message", "user_id"]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    data_type: CommunicationDataType
    message: str
    user_id: int
    def __init__(self, user_id: _Optional[int] = ..., message: _Optional[str] = ..., data_type: _Optional[_Union[CommunicationDataType, str]] = ...) -> None: ...

class CommunicationResponse(_message.Message):
    __slots__ = ["author", "message"]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    author: str
    message: str
    def __init__(self, message: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class FinishDayRequest(_message.Message):
    __slots__ = ["user_id"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class GetUsersResponse(_message.Message):
    __slots__ = ["status", "users"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    status: StatusCode
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, status: _Optional[_Union[StatusCode, str]] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["data", "message", "status"]
    class DataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.ScalarMap[str, str]
    message: str
    status: StatusCode
    def __init__(self, status: _Optional[_Union[StatusCode, str]] = ..., message: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ["name", "user_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    user_id: int
    def __init__(self, user_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class VoteUserRequest(_message.Message):
    __slots__ = ["user_id", "voted_user_id"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    VOTED_USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    voted_user_id: int
    def __init__(self, user_id: _Optional[int] = ..., voted_user_id: _Optional[int] = ...) -> None: ...

class CommunicationDataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
