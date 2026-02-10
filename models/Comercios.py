from helpers.database import db

class Comercio(db.Model):
    __tablename__ = "comercios"

    id = db.Column(db.Integer, primary_key=True)
    nome_comercio = db.Column(db.String(120), nullable=False)
    segmento = db.Column(db.String(80))
    telefone = db.Column(db.String(20), unique=True)
    cnpj = db.Column(db.String(20), unique=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        unique=True  
    )

   
