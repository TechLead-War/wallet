from routes.apis import user
from sanic import Blueprint


blueprint_group = Blueprint.group(
    user
)
