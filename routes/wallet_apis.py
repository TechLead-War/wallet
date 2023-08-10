from datetime import datetime

from sanic import Blueprint
from sanic.request import Request
from tortoise.exceptions import OperationalError

from constants.enums import HTTPStatusCodes, WalletStatus, TransactionStatus
from managers.helpers import send_response, get_user_details, exceptions_handler, wallet_response_formatter, \
    get_wallet_details, to_string
from managers.orm_wrappers import ORMWrapper
from models import Transactions
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
    wallet_instance = {}
    if wallet_instance:
        wallet_details = wallet_instance[0].__dict__
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
    result_json = wallet_response_formatter(user_details, wallet_details.__dict__)
    return await send_response(data=result_json, status_code=HTTPStatusCodes.CREATED.value)


@wallet.route('/wallet', methods=['GET'])
@exceptions_handler
async def get_wallet_balance(request: Request):
    """
        This route is responsible for fetching wallet balance
        based on authentication token given.

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
    """
        This route is responsible for fetching all
         translations of the wallet.
        based on authentication token given.

        Args:
            request: request with Authorization token

        Returns:
            Returns json of resultant data, with these parameters.
              "id": wallet id
              "status": status of wallet
              "type": nature of transaction.
              "amount": balance of the wallet
              "reference_id": unique id of transaction
    """

    auth_token = request.headers.get("Authorization")
    user_details = await get_user_details(auth_token)
    transaction_details = await ORMWrapper.get_by_filters(Transactions, {
        "transaction_from": user_details.get("customer_xid")
    })
    transaction_details_json = []
    for details in transaction_details:
        transaction_details_json.append(to_string(details.__dict__))
    return await send_response(data=transaction_details_json)


# Add virtual money to my wallet
@wallet.route('/wallet/deposits', methods=['POST'])
@exceptions_handler
async def add_wallet_balance(request: Request):
    """
        This route is responsible for adding balance
        in wallet based on auth token and amount given

        Args:
            request: request with Authorization token

        Returns:
            Returns json of resultant data, with these parameters.
              "id": wallet id
              "deposited_by": customer_xid
              "status": status of wallet
              "deposited_at": time of deposit
              "amount": balance of the wallet
              "reference_id": unique id of transaction
    """

    auth_token = request.headers.get("Authorization")
    user_data = request.json
    user_details = await get_user_details(auth_token)

    # fetch wallet details based on customer_xid
    wallet_instance = await ORMWrapper.get_by_filters(Wallet, {
        "customer_xid": user_details.get("customer_xid")
    })
    wallet_details = wallet_instance[0].__dict__
    # if wallet is not active
    if not wallet_details:
        raise ValueError("Wallet not found!")
    if not wallet_details.get("is_enabled"):
        raise OperationalError("Wallet disabled!")

    # update wallet balance
    amount_to_process = user_data.get("amount")

    if amount_to_process <= 0:
        raise OperationalError("invalid amount!")
    final_amount = amount_to_process + wallet_details.get("amount")
    await ORMWrapper.update_with_filters(
        wallet_instance[0],
        Wallet,
        {
            "amount": final_amount,
        }
    )

    # add entry in transactions DB
    reference_id = user_data.get("reference_id")
    transaction_details = await ORMWrapper.create(Transactions, {
        "amount": amount_to_process,
        "status": TransactionStatus.SUCCESS.value,
        "transaction_time": datetime.now(),
        "transaction_from": user_details.get("customer_xid"),
        "transaction_to": "self",
        "transaction_type": TransactionStatus.DEPOSIT.value,
        "reference_id": reference_id,
        "final_amount": final_amount
    })
    transaction_details = transaction_details.__dict__
    result_data = {
        "id": transaction_details.get("id"),
        "deposited_by": user_details.get("customer_xid"),
        "deposited_at": str(transaction_details.get("transaction_time")),
        "amount": amount_to_process,
        "final_amount": final_amount,
        "transaction_type": TransactionStatus.DEPOSIT.value,
        "reference_id": reference_id
    }
    return await send_response(data=result_data)


# Use virtual money from my wallet
@wallet.route('/wallet/withdrawals', methods=['GET'])
@exceptions_handler
async def withdraw_money_from_wallet(request: Request):
    """
        This route is responsible for withdrawal balance
        in wallet based on auth token and amount given

        Args:
            request: request with Authorization token

        Returns:
            Returns json of resultant data, with these parameters.
              "id": wallet id
              "deposited_by": customer_xid
              "status": status of wallet
              "deposited_at": time of deposit
              "amount": balance of the wallet
              "reference_id": unique id of transaction
    """
    auth_token = request.headers.get("Authorization")
    user_data = request.json
    user_details = await get_user_details(auth_token)

    # fetch wallet details based on customer_xid
    wallet_instance = await ORMWrapper.get_by_filters(Wallet, {
        "customer_xid": user_details.get("customer_xid")
    })
    wallet_details = wallet_instance[0].__dict__
    # if wallet is not active
    if not wallet_details:
        raise ValueError("Wallet not found!")
    if not wallet_details.get("is_enabled"):
        raise OperationalError("Wallet disabled!")

    # update wallet balance
    amount_to_process = user_data.get("amount")

    if amount_to_process <= 0:
        raise OperationalError("invalid amount!")

    # if account doesn't have that much balance
    wallet_balance = wallet_details.get("amount")
    if wallet_balance < amount_to_process:
        raise OperationalError("Insufficient balance!")

    final_amount = wallet_details.get("amount") - amount_to_process
    await ORMWrapper.update_with_filters(
        wallet_instance[0],
        Wallet,
        {
            "amount": final_amount,
        }
    )

    # add entry in transactions DB
    reference_id = user_data.get("reference_id")
    transaction_details = await ORMWrapper.create(Transactions, {
        "amount": amount_to_process,
        "status": TransactionStatus.SUCCESS.value,
        "transaction_time": datetime.now(),
        "transaction_from": user_details.get("customer_xid"),
        "transaction_to": "self",
        "reference_id": reference_id
    })
    transaction_details = transaction_details.__dict__
    result_data = {
        "id": transaction_details.get("id"),
        "deposited_by": user_details.get("customer_xid"),
        "deposited_at": str(transaction_details.get("transaction_time")),
        "amount": amount_to_process,
        "final_amount": final_amount,
        "transaction_type": TransactionStatus.WITHDRAWAL.value,
        "reference_id": reference_id
    }
    return await send_response(data=result_data)


@wallet.route('/wallet', methods=['PATCH'])
@exceptions_handler
async def disable_wallet(request: Request):
    """
        This route is responsible for deactivating
        wallet.

        Args:
            request: request with Authorization token

        Returns:
            Returns json of resultant data, with these parameters.
              "id": unique id of wallet
              "owned_by": customer_xid
              "status": status of account
              "disabled_at": time of request
              "balance": amount in the wallet
    """
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
# todo: add postman collections
# todo: add schema diagram, change schema too
