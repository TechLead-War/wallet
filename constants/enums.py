from enum import Enum


class HTTPStatusCodes(Enum):
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    FORBIDDEN = 403
    UNAUTHORIZED = 401
    MOVED_TEMPORARILY = 302
    INTERNAL_SERVER_ERROR = 500
    REQUEST_TIMEOUT = 408


class WalletStatus(Enum):
    ENABLED = True
    DISABLED = False


class TransactionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
