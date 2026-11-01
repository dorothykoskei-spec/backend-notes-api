from marshmallow import Schema, fields,validate
from config import ma
from models.user import User

class UserSchema(ma.SQLAlchemyAutochema):
  class Meta:
    model = User
    load_instance = False
    exclude =('password',)

    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)

    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
user_schema = UserSchema()
users_schema = UserSchema(many=True)