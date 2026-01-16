
from helpers.database import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(11))
    senha = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Usuario {self.email}>"
