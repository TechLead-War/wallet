from sanic import json

from constants.enums import HTTPStatusCodes


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
