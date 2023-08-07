import ujson


from sanic import Sanic, response
from tortoise.contrib.sanic import register_tortoise

app = Sanic(__name__)


@app.route('/')
def ping_route(request):
    return response.json({'message': 'ping route'})


if __name__ == '__main__':
    app.run(debug=True)


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
