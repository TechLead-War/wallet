import uuid
from sanic import Blueprint, response
from sanic.request import Request
from tortoise.exceptions import IntegrityError

from constants.enums import HTTPStatusCodes
from managers.helpers import send_response
from managers.orm_wrappers import ORMWrapper
from models.users import Users

user = Blueprint("user", url_prefix='api/v1')


@user.route('/init', methods=['POST'])
async def init(request: Request):
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
            "data": {
                "error": {
                    "customer_xid": [str(ex)]
                }
            },
            "status": "fail"
        }
        return response.json(result_json, status=400)

    except IntegrityError as e:
        result_json = {
            "error": {
                "customer_xid": [
                    "Missing data for required field."
                ]
            }
        }
        return await send_response(data=result_json, status_code=HTTPStatusCodes.BAD_REQUEST.value)
