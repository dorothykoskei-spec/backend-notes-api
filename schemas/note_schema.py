from marshmallow import Schema, fields, validate


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    content = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    category_id = fields.Int(allow_none=True)
     
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)