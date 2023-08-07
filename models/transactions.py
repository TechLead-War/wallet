from tortoise import Model, fields


class Transactions(Model):
    id = fields.IntField(pk=True)
    amount = fields.IntField()
    status = fields.CharField(max_length=50)
    transaction_time = fields.TimeField(auto_now=True)
    transaction_from = fields.ForeignKeyField('models.Users', to_field='customer_xid')
    transaction_to = fields.ForeignKeyField('models.Users', to_field='customer_xid')
    reference_id = fields.CharField(max_length=50)
