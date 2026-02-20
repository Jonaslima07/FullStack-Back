from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from models.Produtos import Produto
from schema.produtos_schema import ProdutoSchema
from helpers.database import db

produtos_bp = Blueprint("produtos", __name__)

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)


@produtos_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = Produto.query.all()

    hoje = datetime.utcnow().date()
    limite = hoje + timedelta(days=60)

    resultado = []

    for produto in produtos:
        produto_dict = produto_schema.dump(produto)

        if produto.data_validade:
            produto_dict["perto_vencimento"] = (
                hoje <= produto.data_validade <= limite
            )
            produto_dict["vencido"] = (
                produto.data_validade < hoje
            )
        else:
            produto_dict["perto_vencimento"] = False

        resultado.append(produto_dict)

    return jsonify(resultado), 200


@produtos_bp.route("/produtos", methods=["POST"])
def criar_produto():
    try:
        dados = produto_schema.load(request.json)
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    produto = Produto(
        nome = dados["nome"],
        categoria = dados["categoria"],
        quantidade = dados["quantidade"],
        preco = dados["preco"],
        marca = dados["marca"],
        unidade= dados["unidade"], 
        data_validade = dados["data_validade"]
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

