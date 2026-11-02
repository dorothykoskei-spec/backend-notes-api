from marshmallow import Schema, fields, validate, pre_load


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    @pre_load
    def strip_name(self, data, **kwargs):
        if isinstance(data.get("name"), str):
            data["name"] = data["name"].strip()
        return data


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)