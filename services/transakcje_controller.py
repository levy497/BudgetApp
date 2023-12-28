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
            wydatki_data = [
                {
                    "opis": wydatek.opis,
                    "kwota": str(wydatek.kwota),
                    "data_transakcji": wydatek.data_transakcji.strftime('%Y-%m-%d'),
                    "typ": wydatek.typ,
                    "id": wydatek.id
                }
                for wydatek in wydatki
            ]
            return wydatki_data, 200
        except Exception as e:
            return {"message": "Error", "error": str(e)}, 500

    @staticmethod
    def delete_wydatek(id):
        wydatek = Transakcja.query.get(id)
        if not wydatek:
            return jsonify({'message': 'Wydatek not found'}), 404

        try:
            # Aktualizacja budżetu przed usunięciem wydatku
            miesiac, rok = wydatek.data_transakcji.month, wydatek.data_transakcji.year
            budzet = Budzet.query.filter_by(
                uzytkownik_id=wydatek.uzytkownik_id,
                kategoria_id=wydatek.kategoria_id,
                miesiac=miesiac,
                rok=rok
            ).first()

            if budzet:
                if wydatek.typ == 'przychod':
                    budzet.kwota -= wydatek.kwota  # Odejmij kwotę przychodu
                elif wydatek.typ == 'wydatek':
                    budzet.kwota += wydatek.kwota  # Dodaj kwotę wydatku

            db.session.delete(wydatek)
            db.session.commit()

            return jsonify({'message': 'Wydatek deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error", "error": str(e)}), 500
    @staticmethod
    def edit_wydatek(id):
        data = request.get_json()
        wydatek = Transakcja.query.get(id)
        if not wydatek:
            return jsonify({'message': 'Wydatek not found'}), 404

        try:
            # Zapisz oryginalną kwotę i typ przed dokonaniem aktualizacji
            original_kwota = wydatek.kwota
            original_typ = wydatek.typ

            # Aktualizacja danych wydatku
            wydatek.opis = data['opis']
            wydatek.kwota = decimal.Decimal(data['kwota'])
            wydatek.typ = data['typ']

            # Aktualizuj budżet
            miesiac, rok = wydatek.data_transakcji.month, wydatek.data_transakcji.year
            budzet = Budzet.query.filter_by(
                uzytkownik_id=wydatek.uzytkownik_id,
                kategoria_id=wydatek.kategoria_id,
                miesiac=miesiac,
                rok=rok
            ).first()

            if budzet:
                # Odwróć oryginalną transakcję
                if original_typ == 'przychod':
                    budzet.kwota -= original_kwota
                else:
                    budzet.kwota += original_kwota

                # Zastosuj nową transakcję
                if wydatek.typ == 'przychod':
                    budzet.kwota += wydatek.kwota
                else:
                    budzet.kwota -= wydatek.kwota

            db.session.commit()
            return jsonify({'message': 'Wydatek updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error", "error": str(e)}), 500
