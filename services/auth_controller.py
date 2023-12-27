from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from models.models import Uzytkownik
from __init__ import db

class AuthController:
    @staticmethod
    def register(email, password, nick):
        # Sprawdź, czy użytkownik już istnieje
        existing_user = Uzytkownik.query.filter_by(email=email).first()
        if existing_user:
            return {"message": "Użytkownik z tym adresem email już istnieje."}, 400

        # Hashowanie hasła
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Utworzenie nowego użytkownika
        new_user = Uzytkownik(email=email, haslo=hashed_password, nick=nick)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "Użytkownik zarejestrowany pomyślnie."}, 201

    @staticmethod
    def login(data):
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        email = data['email']
        password = data['password']

        if not email or not password:
            return jsonify({"msg": "Missing email or password"}), 400

        user = Uzytkownik.query.filter_by(email=email).first()
        if not user:
            return jsonify({"msg": "Email not found"}), 404

        if not check_password_hash(user.haslo, password):
            return jsonify({"msg": "Wrong password"}), 401

        access_token = create_access_token(identity={'email': user.email, 'id': user.id})
        refresh_token = create_refresh_token(identity={'email': user.email, 'id': user.id})

        return jsonify(access_token=access_token, refresh_token=refresh_token, msg="Login successful"), 200

    @staticmethod
    def status():
        current_user_email = get_jwt_identity()['email']
        user = Uzytkownik.query.filter_by(email=current_user_email).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404

        return {
            "logged_in_as": user.email,
            "nick": user.nick
        }, 200


