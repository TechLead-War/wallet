from tortoise import Model, fields


class Wallet(Model):
    id = fields.IntField(pk=True)
    amount = fields.IntField()
    customer_xid = fields.ForeignKeyField('models.Users', to_field='customer_xid')
    enabled_at = fields.TimeField()
    is_enabled = fields.BooleanField(default=False)
