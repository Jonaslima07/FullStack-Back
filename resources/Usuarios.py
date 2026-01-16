from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError

from models.Usuarios import Usuario
from schema.usuario_schema import UsuarioSchema
from helpers.database import db

# Blueprint
usuarios_bp = Blueprint("usuarios", __name__)

# Schemas
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)


@usuarios_bp.route("/usuarios", methods=["GET"])
def capturar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(usuarios)), 200


@usuarios_bp.route("/usuarios/<int:id>", methods=["GET"])
def capturar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return usuario_schema.dump(usuario), 200


@usuarios_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    try:
        # Validação + desserialização
        dados = usuario_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Criação do usuário
    usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
        cpf=dados.get("cpf"),
        senha=generate_password_hash(dados["senha"])
    )

    # Persistência
    db.session.add(usuario)
    db.session.commit()

    # Resposta (sem senha)
    return usuario_schema.dump(usuario), 201


@usuarios_bp.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        # partial=True → não exige todos os campos
        dados = usuario_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Atualização dos campos permitidos
    if "nome" in dados:
        usuario.nome = dados["nome"]

    if "email" in dados:
        usuario.email = dados["email"]

    if "cpf" in dados:
        usuario.cpf = dados["cpf"]

    if "senha" in dados:
        usuario.senha = generate_password_hash(dados["senha"])

    db.session.commit()

    return usuario_schema.dump(usuario), 200
