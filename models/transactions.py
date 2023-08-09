from tortoise import Model, fields


class Transactions(Model):
    id = fields.IntField(pk=True)
    amount = fields.IntField()
    final_amount = fields.IntField()
    status = fields.CharField(max_length=50)
    transaction_time = fields.DatetimeField(auto_now=True)
    transaction_from = fields.CharField(max_length=50)
    transaction_to = fields.CharField(max_length=50)
    transaction_type = fields.CharField(max_length=50)
    reference_id = fields.CharField(max_length=50)
