from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from models.Comercios import Comercio
from schema.comercio_schema import ComercioSchema
from helpers.database import db
from extensions.cache import cache

comercios_bp = Blueprint("comercios", __name__)

comercio_schema = ComercioSchema()
comercios_schema = ComercioSchema(many=True)


@comercios_bp.route("/comercios", methods=["GET"])
def buscar_comercios():
    cache_key = "comercios:lista"

   
    comercios_cache = cache.get(cache_key)

    if comercios_cache:
        return jsonify({
            "origem": "redis",
            "dados": comercios_cache
        }), 200

    
    comercios = Comercio.query.all()
    dados = comercios_schema.dump(comercios)

    
    cache.set(cache_key, dados, timeout=120)

    return jsonify({
        "origem": "banco",
        "dados": dados
    }), 200

@comercios_bp.route("/comercios", methods=["POST"])
def criar_comercio():
    try:
        dados = comercio_schema.load(request.json)

    except ValidationError as err:
        print("ERROS DO MARSHMALLOW:", err.messages)
        return jsonify(err.messages), 400
    
    comercio = Comercio(
        nome_comercio = dados["nome_comercio"],
        segmento = dados["segmento"],
        telefone = dados["telefone"],
        cnpj = dados["cnpj"],
        
    )

    db.session.add(comercio)
    db.session.commit()

    return comercio_schema.dump(comercio), 201

@comercios_bp.route("/comercios/<int:id>", methods=["PUT"])
def atualizar_comercios(id):
    comercios = Comercio.query.get_or_404(id)
    try:
        dados = comercio_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if "nome_comercio" in dados:
        comercios.nome = dados["nome_comercio"]

    if "segmento" in dados:
        comercios.segmento = dados["segmento"]

    if "telefone" in dados:
        comercios.telefone = dados["telefone"]

    if "cnpj" in dados:
        comercios.cnpj = dados["cnpj"]

    

    db.session.commit()

    return comercio_schema.dump(comercios), 200

@comercios_bp.route("/comercios/<int:id>", methods=["DELETE"])
def delete(id):
    comercio = Comercio.query.get(id)

    if not comercio:
        return jsonify({"error: comércio não encontrado"}), 404
    
    db.session.delete(comercio)
    db.session.commit()

    return jsonify({"message": "Comércio removido com sucesso"}), 200
