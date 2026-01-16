from helpers.database import db


class Comercio(db.Model):
    __tablename__ = "comercios"

    id = db.Column(db.Integer, primary_key=True)
    nome_comercio = db.Column(db.String(100), nullable=False)
    segmento = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True)

    cadastro_completo = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Comercio {self.nome_comercio}>"
