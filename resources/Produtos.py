from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from models.Produtos import Produto
from models.Usuarios import Usuario
from schema.produtos_schema import ProdutoSchema
from helpers.database import db

produtos_bp = Blueprint("produtos", __name__)

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)



@produtos_bp.route("/produtos", methods=["GET"])
@jwt_required()
def listar_produtos():

    user_id = int(get_jwt_identity())

    usuario = Usuario.query.get(user_id)

    if not usuario:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    produtos = Produto.query.filter_by(
        comercio_id=usuario.comercio_id
    ).all()

    lista = []

    for p in produtos:
        lista.append({
            "id": p.id,
            "nome": p.nome,
            "marca": p.marca,
            "categoria": p.categoria,
            "quantidade": p.quantidade,
            "preco": p.preco,
            "unidade": p.unidade,
            "data_validade": str(p.data_validade)
        })

    return jsonify(lista), 200

@produtos_bp.route("/produtos", methods=["POST"])
@jwt_required()
def criar_produto():

    try:
        dados = produto_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_id = int(get_jwt_identity())

    usuario = Usuario.query.get(user_id)

    if not usuario:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    if not usuario.comercio_id:
        return jsonify({"msg": "Usuário sem comércio"}), 400

    comercio_id = usuario.comercio_id

    produto = Produto(
        nome=dados["nome"],
        categoria=dados["categoria"],
        quantidade=dados["quantidade"],
        preco=dados["preco"],
        marca=dados["marca"],
        unidade=dados["unidade"],
        data_validade=dados["data_validade"],
        comercio_id=comercio_id
    )

    db.session.add(produto)
    db.session.commit()

    return produto_schema.dump(produto), 201
@produtos_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produtos(id):

    produtos = Produto.query.get_or_404(id)

    try:
        dados = produto_schema.load(request.json, partial=True)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if "nome" in dados:
        produtos.nome = dados["nome"]

    if "categoria" in dados:
        produtos.categoria = dados["categoria"]

    if "quantidade" in dados:
        produtos.quantidade = dados["quantidade"]

    if "preco" in dados:
        produtos.preco = dados["preco"]

    if "marca" in dados:
        produtos.marca = dados["marca"]

    if "unidade" in dados:
        produtos.unidade = dados["unidade"]
    
    if "data_validade" in dados:
        produtos.data_validade = dados["data_validade"]

    db.session.commit()

    return produto_schema.dump(produtos), 200

@produtos_bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"message": "Produto removido com sucesso"}), 200

