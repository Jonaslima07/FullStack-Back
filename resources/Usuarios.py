from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from marshmallow import ValidationError

from models.Usuarios import Usuario
from schema.usuario_schema import UsuarioSchema
from schema.completarCadastro_schema import CompletarCadastroSchema
from helpers.database import db

usuarios_bp = Blueprint("usuarios", __name__)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
completar_schema = CompletarCadastroSchema()



@usuarios_bp.route("/usuarios", methods=["GET"])
def capturar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(usuarios)), 200


@usuarios_bp.route("/usuarios/me", methods=["GET"])
@jwt_required()
def obter_usuario_logado():
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.get(user_id)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify(usuario_schema.dump(usuario)), 200




@usuarios_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    try:
        dados = usuario_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
        cpf=dados.get("cpf"),
        senha=generate_password_hash(dados["senha"]),
        cadastro_completo=True
    )

    db.session.add(usuario)
    db.session.commit()

    return usuario_schema.dump(usuario), 201



@usuarios_bp.route("/usuarios/completar-cadastro", methods=["POST"])
@jwt_required()
def completar_cadastro():
    dados = request.get_json() or {}

    cpf = dados.get("cpf")
    senha = dados.get("senha")

    if not cpf or not senha:
        return jsonify({"error": "CPF e senha são obrigatórios"}), 400

    user_id = int(get_jwt_identity())  
    usuario = Usuario.query.get(user_id)
  

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if usuario.cadastro_completo:
        return jsonify({"error": "Cadastro já completo"}), 400

    usuario.cpf = cpf
    usuario.senha = generate_password_hash(senha)
    usuario.cadastro_completo = True

    db.session.commit()

    return jsonify({"message": "Cadastro completado com sucesso"}), 200



@usuarios_bp.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        dados = usuario_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

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



@usuarios_bp.route("/usuarios/<int:id>", methods=["DELETE"])
def deletar_usuario(id):
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "Usuário deletado com sucesso"}), 200
