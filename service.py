from datetime import datetime
from urllib.request import Request

import aiofiles
import ujson
from sanic import Sanic, response
from tortoise.contrib.sanic import register_tortoise

from routes import blueprint_group


app = Sanic(name='Draipe')
app.blueprint(blueprint_group)


for route in app.router.routes:
    print(f"/{route.path} ")


@app.route('/')
def ping_route(request):
    return response.json({'message': 'ping route'})


if __name__ == '__main__':
    app.run(debug=True)


async def log_request(request: Request):
    """
        This functions logs all incoming request in request.log file.
    """

    async with aiofiles.open('request.log', 'a') as f:
        await f.write(f"Request method: {request.method}\n")
        await f.write(f"Request Host: {request.headers.get('Host')}\n")
        await f.write(f"Request URL: {request.url}\n")
        await f.write(f"Request headers: {request.headers}\n")
        await f.write(f"Request data: {request.json}\n")
        await f.write(f"Request time: {datetime.now()}\n\n")


@app.middleware('request')
async def call_logger(request: Request):

    """
        This is a middleware which logs all incoming requests
        and store all requests in request.log file in async
        manner.
    """
    await log_request(request)


def json_file_to_dict(_file: str) -> dict:
    """
        This function converts a Json 'file' to a dict.

        Args:
            _file: path of the json file.
        Returns:
            Converted dict converted from json.
    """

    config = None
    try:
        with open(_file) as config_file:
            config = ujson.load(config_file)
    except (TypeError, FileNotFoundError, ValueError) as exception:
        print(exception)

    return config


class CONFIG:
    config = json_file_to_dict("config.json")


register_tortoise(
    app, db_url=CONFIG.config["DB_URL"],
    modules={"models": ["models"]},
    generate_schemas=True
)
