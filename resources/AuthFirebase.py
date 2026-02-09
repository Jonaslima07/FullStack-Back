from flask import Blueprint, request, jsonify
from firebase_admin import auth as firebase_auth
from flask_jwt_extended import create_access_token
from models.Usuarios import Usuario
from helpers.database import db

authFirebase_bp = Blueprint("authFirebase", __name__)

@authFirebase_bp.route("/auth/google", methods=["POST"])
def auth_google():
    data = request.get_json()

    if not data or "idToken" not in data:
        return jsonify({"error": "Token do Firebase não enviado"}), 400

    try:
        decoded = firebase_auth.verify_id_token(data["idToken"])

        email = decoded.get("email")
        nome = decoded.get("name", "Usuário Google")

        if not email:
            return jsonify({"error": "Email não encontrado no token"}), 400

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha=None,
                cadastro_completo=False
            )
            db.session.add(usuario)
            db.session.commit()

        access_token = create_access_token(identity=str(usuario.id))

        print("TOKEN GERADO:", access_token)

        return jsonify({
            "token": access_token,
            "user": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "cpf": usuario.cpf,
                "cadastro_completo": usuario.cadastro_completo
            }
        }), 200



    except firebase_auth.ExpiredIdTokenError:
        return jsonify({"error": "Token Firebase expirado"}), 401

    except firebase_auth.InvalidIdTokenError:
        return jsonify({"error": "Token Firebase inválido"}), 401

    except Exception as e:
        db.session.rollback()
        print("🔥 ERRO AUTH GOOGLE:", e)
        return jsonify({"error": "Erro interno no servidor"}), 500
