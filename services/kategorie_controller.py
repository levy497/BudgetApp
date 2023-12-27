from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from __init__ import db
from models.models import Kategoria

class KategorieController:
    @staticmethod
    def add_kategoria(data):
        current_user_id = get_jwt_identity()['id']  # Pobierz ID zalogowanego użytkownika z tokena JWT
        nazwa = data.get('nazwa')
        typ = data.get('typ')

        if not nazwa or not typ:
            return jsonify({"message": "Brak nazwy lub typu kategorii"}), 400

        nowa_kategoria = Kategoria(nazwa=nazwa, typ=typ, uzytkownik_id=current_user_id)
        db.session.add(nowa_kategoria)
        db.session.commit()

        return jsonify({"message": "Kategoria dodana pomyślnie"}), 201

    @staticmethod
    def get_kategorie():
        current_user_id = get_jwt_identity()['id']

        kategorie = Kategoria.query.filter_by(uzytkownik_id=current_user_id).all()
        kategorie_data = [{"id": kategoria.id, "nazwa": kategoria.nazwa, "typ": kategoria.typ} for kategoria in
                          kategorie]

        return jsonify(kategorie_data), 200
