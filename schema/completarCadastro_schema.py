from marshmallow import Schema, fields

class CompletarCadastroSchema(Schema):
    cpf = fields.String(required=True)
    senha = fields.String(required=True)
