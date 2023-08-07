from tortoise import Model, fields


class Users(Model):
    id = fields.IntField(pk=True)
    customer_xid = fields.CharField(max_length=50)
    token = fields.CharField(max_length=50)
