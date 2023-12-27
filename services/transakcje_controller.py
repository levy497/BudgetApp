from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from __init__ import db
from models.models import Budzet, Transakcja, Kategoria, Uzytkownik
import decimal

class TransakcjeController:
    @staticmethod
    def add_wydatek():
        current_user_email = get_jwt_identity()['email']
        user = Uzytkownik.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({"msg": "User not found"}), 404

        try:
            data = request.get_json()
            kwota = decimal.Decimal(data['kwota'])
            opis = data.get('opis', '')
            kategoria_id = data['kategoria_id']
            data_transakcji = datetime.strptime(data['data_transakcji'], '%Y-%m-%d').date()
            typ_transakcji = data.get('typ', 'wydatek')  # domyślnie 'wydatek'

            kategoria = Kategoria.query.filter_by(id=kategoria_id).first()
            if not kategoria:
                return jsonify({"msg": "Kategoria not found"}), 404

            nowa_transakcja = Transakcja(
                uzytkownik_id=user.id,
                kategoria_id=kategoria_id,
                opis=opis,
                kwota=kwota,
                data_transakcji=data_transakcji,
                typ=typ_transakcji
            )
            db.session.add(nowa_transakcja)

            miesiac, rok = data_transakcji.month, data_transakcji.year
            budzet = Budzet.query.filter_by(
                uzytkownik_id=user.id,
                kategoria_id=kategoria_id,
                miesiac=miesiac,
                rok=rok
            ).first()

            # Aktualizuj budżet w zależności od typu transakcji
            if typ_transakcji == 'przychod':
                if budzet:
                    budzet.kwota += kwota
                else:
                    nowy_budzet = Budzet(
                        uzytkownik_id=user.id,
                        kategoria_id=kategoria_id,
                        kwota=kwota,
                        miesiac=miesiac,
                        rok=rok
                    )
                    db.session.add(nowy_budzet)
            elif typ_transakcji == 'wydatek':
                if budzet:
                    budzet.kwota -= kwota
                else:
                    nowy_budzet = Budzet(
                        uzytkownik_id=user.id,
                        kategoria_id=kategoria_id,
                        kwota=-kwota,
                        miesiac=miesiac,
                        rok=rok
                    )
                    db.session.add(nowy_budzet)

            db.session.commit()

            return jsonify({"msg": "Transakcja dodana pomyślnie"}), 201
        except Exception as e:
            return jsonify({"msg": "Error", "error": str(e)}), 500

    @staticmethod
    def get_wydatki(user_id):
        try:
            wydatki = Transakcja.query.filter_by(uzytkownik_id=user_id).all()
            wydatki_data = [{"opis": wydatek.opis, "kwota": str(wydatek.kwota), "data_transakcji": wydatek.data_transakcji.strftime('%Y-%m-%d')} for wydatek in wydatki]
            return wydatki_data, 200
        except Exception as e:
            return {"message": "Error", "error": str(e)}, 500


