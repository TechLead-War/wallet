import uuid
from datetime import datetime

from sanic import Blueprint, response
from sanic.request import Request
from tortoise.exceptions import IntegrityError, ValidationError, OperationalError

from constants.enums import HTTPStatusCodes, WalletStatus
from managers.helpers import send_response
from managers.orm_wrappers import ORMWrapper
from models.users import Users
from models.wallet import Wallet

user = Blueprint("user", url_prefix='api/v1')


@user.route('/init', methods=['POST'])
async def init(request: Request):
    """
        This route is responsible for initialization of user in our
        wallet service, this creates the users and generates a token
        to be consumed further by user. (instance created in user DB).

        Args:
            request: request with customer_xid

        Returns:
            json: resultant data of request, failure or success response.
    """

    try:
        new_token = str(uuid.uuid4())

        data = request.json
        if not data or not isinstance(data, dict) or not data.get('customer_xid'):
            raise ValueError('Missing or invalid data for required field.')

        customer_xid = data['customer_xid']

        # Create user in the database
        await ORMWrapper.create(Users, {
            "customer_xid": customer_xid,
            "token": new_token
        })
        result_json = {
            "token": "Token " + new_token,
        }

        return await send_response(data=result_json, status_code=HTTPStatusCodes.CREATED.value)

    except ValueError as ex:
        result_json = {
            "error": {
                "customer_xid": [
                    "Missing data for required field."
                ]
            }
        }
        return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)

    except IntegrityError as e:
        result_json = {
            "error": {
                "customer_xid": [
                    "User with this customer_xid already exists."
                ]
            }
        }
        return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)
