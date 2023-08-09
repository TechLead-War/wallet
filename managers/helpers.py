from functools import wraps

from sanic import json, response
from tortoise.exceptions import OperationalError, IntegrityError

from constants.enums import HTTPStatusCodes, WalletStatus
from managers.orm_wrappers import ORMWrapper
from models import Users, Wallet


async def send_response(data=None, status_code=HTTPStatusCodes.SUCCESS.value,
                        meta=None, body: dict = None, headers=None, purge_response_keys=False):
    """
        :param data: final response data
        :param status_code: success status code, default is 200
        :param body: Optional: Response body dict in v4 format.
        :param headers: Optional : Response headers to be sent to clients.
        :param purge_response_keys: Optional : Converts response into dict
        :param meta results
        :return {'data': data, status: status, 'status_code': status_code}

    """

    if body is not None:
        return json(body=body, status=body["status_code"])

    status_code = status_code
    status = "success" if status_code in [200, 201] else "fail"
    data = {"data": data, "status": status, "status_code": status_code}
    if meta:
        data["meta"] = meta
    if purge_response_keys:  # if no formatting requested just data is needed
        return data
    return json(body=data, status=status_code, headers=headers)


async def get_user_details(auth_token: str):
    if not auth_token:
        raise ValueError('Missing or invalid data for required field.')

    # check the format of token
    token = auth_token.split(" ")
    if token[0] != "Token":
        raise OperationalError("Invalid Token format")

    # get details of the user based on this token
    token = token[1]
    user_details = await ORMWrapper.get_by_filters(Users, filters={
        "token": token
    })
    if not user_details:
        raise OperationalError()
    return user_details[0].__dict__


async def get_wallet_details(user_details):
    wallet_details = await ORMWrapper.get_by_filters(Wallet,
                                                     filters={
                                                         "customer_xid": user_details.get("customer_xid")
                                                     })
    if not wallet_details:
        raise OperationalError()

    return wallet_details[0].__dict__


def wallet_response_formatter(user_details: dict, wallet_details: dict):
    return {
        "id": wallet_details.get("id"),
        "owned_by": user_details.get("customer_xid"),
        "status": wallet_details.get("is_enabled") or WalletStatus.ENABLED.value,
        "enabled_at": str(wallet_details.get("enabled_at")),
        "balance": wallet_details.get("amount")
    }


def dict_to_model_instance(data_dict, model_class):
    model_instance = model_class()
    for key, value in data_dict.items():
        if hasattr(model_instance, key):
            setattr(model_instance, key, value)
    return model_instance


def exceptions_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except IntegrityError as ex:
            result_json = {
                "error": "Already enabled"
            }
            return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)

        except OperationalError as ex:
            result_json = {
                "error": "Invalid token!!!"
            }
            return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)

        except ValueError as ex:
            result_json = {
                "error": str(ex)
            }
            return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)

    return wrapper
