from enum import Enum


class ErrorCode(Enum):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
