from marshmallow import Schema, fields, validate

class ComercioSchema(Schema):
    id = fields.Int(dump_only=True)

    nome_comercio = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100)
    )

    segmento = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100)
    )

    telefone = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=11)
    )

    cnpj = fields.Str(
        required=True,
        validate=validate.Length(equal=14)
    )


    cadastro_completo = fields.Bool(required=True)