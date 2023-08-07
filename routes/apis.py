import uuid
from sanic import Blueprint, response
from sanic.request import Request

from managers.orm_wrappers import ORMWrapper
from models.users import Users

user = Blueprint("user")


@user.route('/api/v1/init', methods=['POST'])
async def init(request: Request):
    try:
        data = request.json
        customer_xid = data.get('customer_xid')

        new_token = str(uuid.uuid4())

        # create user in our database
        await ORMWrapper.create(Users, {
            "customer_xid": customer_xid,
            "token": new_token
        })

        result_json = {
            "data": {
                "token": new_token
            },
            "status": "success"
        }

        return response.json(result_json)

    except Exception as e:
        result_json = {
            "data": {
                "message": str(e)
            },
            "status": "error"
        }
        return response.json(result_json)
