from tortoise import Model, fields


class Wallet(Model):
    id = fields.IntField(pk=True)
    amount = fields.IntField()
    customer_xid = fields.CharField(max_length=50)
    enabled_at = fields.TimeField()
    is_enabled = fields.BooleanField(default=False)
