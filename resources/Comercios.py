from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models.Comercios import Comercio
from schema.comercio_schema import ComercioSchema
from helpers.database import db
from extensions.cache import cache

comercios_bp = Blueprint("comercios", __name__)

comercio_schema = ComercioSchema()
comercios_schema = ComercioSchema(many=True)


# =========================
# GET - LISTAR COMÉRCIOS
# =========================
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


# =========================
# POST - CRIAR COMÉRCIO
# =========================
@comercios_bp.route("/comercios", methods=["POST"])
def criar_comercio():
    try:
        dados = comercio_schema.load(request.json)

        nome = dados["nome_comercio"]
        telefone = dados["telefone"]
        cnpj = dados["cnpj"]

        # 🔒 Valida duplicados
        if Comercio.query.filter_by(nome_comercio=nome).first():
            return jsonify({"msg": "Já existe um comércio com esse nome"}), 409

        if Comercio.query.filter_by(telefone=telefone).first():
            return jsonify({"msg": "Já existe um comércio com esse telefone"}), 409

        if Comercio.query.filter_by(cnpj=cnpj).first():
            return jsonify({"msg": "Já existe um comércio com esse CNPJ"}), 409

        comercio = Comercio(
            nome_comercio=nome,
            segmento=dados["segmento"],
            telefone=telefone,
            cnpj=cnpj,
            cadastro_completo=False
        )

        db.session.add(comercio)
        db.session.commit()

        # 🧹 limpa cache
        cache.delete("comercios:lista")

        return comercio_schema.dump(comercio), 201

    except ValidationError as err:
        return jsonify(err.messages), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "msg": "Erro de integridade: dados já cadastrados"
        }), 409


# =========================
# PUT - ATUALIZAR COMÉRCIO
# =========================
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


# =========================
# DELETE - REMOVER COMÉRCIO
# =========================
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
