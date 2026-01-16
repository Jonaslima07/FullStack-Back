from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)

    nome = fields.Str(
        required=True,
        validate=validate.Length(min=3)
    )

    email = fields.Email(required=True)

    cpf = fields.Str(
        validate=validate.Length(equal=11)
    )

    senha = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=6)
    )

    confirmarSenha = fields.Str(
        required=True,
        load_only=True
    )

    @validates_schema
    def validar_senhas(self, data, **kwargs):
        if data.get("senha") != data.get("confirmarSenha"):
            raise ValidationError(
                {"confirmarSenha": ["As senhas não conferem"]}
            )
