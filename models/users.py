from tortoise import Model, fields


class Users(Model):
    id = fields.IntField(pk=True)
    customer_xid = fields.CharField(max_length=50, unique=True)
    token = fields.CharField(max_length=50)
