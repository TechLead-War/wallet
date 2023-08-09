from routes.apis import user
from routes.wallet_apis import wallet
from sanic import Blueprint


blueprint_group = Blueprint.group(
    user,
    wallet
)
