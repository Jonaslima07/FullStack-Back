from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity


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



@comercios_bp.route("/comercios/me", methods=["GET"])
@jwt_required()
def meu_comercio():
    usuario_id = get_jwt_identity()

    comercio = Comercio.query.filter_by(usuario_id=usuario_id).first()

    if not comercio:
        return jsonify({"has_comercio": False}), 200

    return jsonify({
        "has_comercio": True,
        "comercio": {
            "id": comercio.id,
            "nome_comercio": comercio.nome_comercio
        }
    }), 200



@comercios_bp.route("/comercios", methods=["POST"])
@jwt_required()
def criar_comercio():
    try:
        user_id = int(get_jwt_identity())
        dados = comercio_schema.load(request.json)

       
        comercio_existente = Comercio.query.filter_by(
            usuario_id=user_id
        ).first()

        if comercio_existente:
            return jsonify({
                "msg": "Este usuário já possui um comércio cadastrado"
            }), 400

        comercio = Comercio(
            nome_comercio=dados["nome_comercio"],
            segmento=dados.get("segmento"),
            telefone=dados["telefone"],
            cnpj=dados["cnpj"],
            usuario_id=user_id, 
            
        )

        db.session.add(comercio)
        db.session.commit()

        cache.delete("comercios:lista")

        return comercio_schema.dump(comercio), 201

    except ValidationError as err:
        return jsonify(err.messages), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "msg": "Telefone ou CNPJ já cadastrado"
        }), 409


@comercios_bp.route("/comercios/<int:id>", methods=["PUT"])
def atualizar_comercio(id):
    comercio = Comercio.query.get_or_404(id)

    try:
        dados = comercio_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if "nome_comercio" in dados:
        comercio.nome_comercio = dados["nome_comercio"]

    if "segmento" in dados:
        comercio.segmento = dados["segmento"]

    if "telefone" in dados:
        comercio.telefone = dados["telefone"]

    if "cnpj" in dados:
        comercio.cnpj = dados["cnpj"]

    try:
        db.session.commit()
        cache.delete("comercios:lista")
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "msg": "Telefone ou CNPJ já cadastrado"
        }), 409

    return comercio_schema.dump(comercio), 200




@comercios_bp.route("/comercios/<int:id>", methods=["DELETE"])
def deletar_comercio(id):
    comercio = Comercio.query.get(id)

    if not comercio:
        return jsonify({"msg": "Comércio não encontrado"}), 404

    db.session.delete(comercio)
    db.session.commit()

    cache.delete("comercios:lista")

    return jsonify({
        "msg": "Comércio removido com sucesso"
    }), 200
