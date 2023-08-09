from datetime import datetime

from sanic import Blueprint, response
from sanic.request import Request
from tortoise.exceptions import IntegrityError, OperationalError

from constants.enums import HTTPStatusCodes, WalletStatus
from managers.helpers import send_response, get_user_details, exceptions_handler, wallet_response_formatter, \
    get_wallet_details, dict_to_model_instance
from managers.orm_wrappers import ORMWrapper
from models.users import Users
from models.wallet import Wallet

wallet = Blueprint("wallet", url_prefix='api/v1')


@wallet.route('/wallet', methods=['POST'])
@exceptions_handler
async def init_wallet(request: Request):
    """
        This route is responsible for creating a virtual wallet for
        a user, it offers an instance of wallet in wallet db.
        and enable the wallet if in inactive state.

        Args:
            request: request with Authorization token

        Returns:
            Returns json of resultant data, with these parameters.
              "id": wallet id
              "owned_by": user id
              "status": status of wallet
              "enabled_at": time of last activation request.
              "balance": balance of the wallet
    """

    # if wallet of this user is already active return failure.
    auth_token = request.headers.get("Authorization")
    user_details = await get_user_details(auth_token)

    # check if wallet already present with this customer_xid
    wallet_instance = await ORMWrapper.get_by_filters(Wallet, {
        "customer_xid": user_details.get("customer_xid")
    })
    wallet_details = wallet_instance[0].__dict__
    if wallet_details:
        await ORMWrapper.update_with_filters(
            wallet_instance[0],
            Wallet,
            {
                "is_enabled": WalletStatus.ENABLED.value,
            }
        )
    else:
        # Create wallet for the user in database
        wallet_details = await ORMWrapper.create(Wallet, {
            "is_enabled": True,
            "amount": 110,
            "customer_xid": user_details.get("customer_xid"),
            "enabled_at": datetime.now(),
        })

    result_json = wallet_response_formatter(user_details, wallet_details)
    return await send_response(data=result_json, status_code=HTTPStatusCodes.CREATED.value)


@wallet.route('/wallet', methods=['GET'])
@exceptions_handler
async def get_wallet_balance(request: Request):
    # if token wrong or not given
    auth_token = request.headers.get("Authorization")
    user_details = await get_user_details(auth_token)

    # fetch wallet details based on customer_xid
    wallet_details = await get_wallet_details(user_details)
    if not wallet_details:
        raise OperationalError()

    # if wallet is not active
    if not wallet_details.get("is_enabled"):
        raise ValueError("Wallet disabled!")

    # send wallet details
    result_json = wallet_response_formatter(user_details, wallet_details)
    return await send_response(data=result_json, status_code=HTTPStatusCodes.SUCCESS.value)


# View my wallet transactions

@wallet.route('/wallet/transactions', methods=['GET'])
async def get_wallet_transactions(request: Request):
    pass


# Add virtual money to my wallet
@wallet.route('/wallet/deposits', methods=['GET'])
@exceptions_handler
async def add_wallet_balance(request: Request):
    # if wallet doesn't exist
    # if token wrong or not given
    auth_token = request.headers.get("Authorization")
    user_details = await get_user_details(auth_token)
    wallet_details = await get_wallet_details(user_details)
    # if wallet is not active
    if not wallet_details.get("is_enabled"):
        raise OperationalError("Wallet disabled!")
    # todo: complete this function


# Use virtual money from my wallet
@wallet.route('/wallet/withdrawals', methods=['GET'])
@exceptions_handler
async def withdraw_money_from_wallet(request: Request):
    pass


@wallet.route('/wallet', methods=['PATCH'])
@exceptions_handler
async def disable_wallet(request: Request):
    # if token wrong or not given
    auth_token = request.headers.get("Authorization")
    user_details = await get_user_details(auth_token)

    # fetch wallet details based on customer_xid
    wallet_instance = await ORMWrapper.get_by_filters(Wallet, {
        "customer_xid": user_details.get("customer_xid")
    })
    wallet_details = wallet_instance[0].__dict__
    if not wallet_details:
        raise OperationalError()

    # if wallet is already disabled
    if not wallet_details.get("is_enabled"):
        raise ValueError("Wallet disabled!")

    # update wallet details - disable wallet
    await ORMWrapper.update_with_filters(
        wallet_instance[0],
        Wallet,
        {
            "is_enabled": WalletStatus.DISABLED.value,
        }
    )
    wallet_details["is_enabled"] = WalletStatus.DISABLED.value
    result_json = wallet_response_formatter(user_details, wallet_details)
    return await send_response(data=result_json, status_code=HTTPStatusCodes.SUCCESS.value)



# todo: segregate models and routes, MVC required.
