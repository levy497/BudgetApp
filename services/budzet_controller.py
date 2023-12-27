from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import extract
from models.models import Budzet


class BudgetController:
    @staticmethod
    def get_budget():
        current_user_id = get_jwt_identity()['id']  # Załóżmy, że identity zwraca ID użytkownika
        # Pobieranie parametrów z zapytania, jeśli nie są dostarczone używamy bieżącego miesiąca i roku
        miesiac = request.args.get('miesiac', default=datetime.now().month, type=int)
        rok = request.args.get('rok', default=datetime.now().year, type=int)

        try:
            budget = Budzet.query.filter(
                Budzet.uzytkownik_id == current_user_id,
                Budzet.miesiac == miesiac,
                Budzet.rok == rok
            ).all()

            budget_data = [{
                'id': b.id,
                'kategoria_id': b.kategoria_id,
                'kwota': str(b.kwota),  # DECIMAL musi być przekształcony na string do JSON
                'miesiac': b.miesiac,
                'rok': b.rok
            } for b in budget]

            return jsonify(budget_data), 200
        except Exception as e:
            return jsonify({'msg': str(e)}), 500

