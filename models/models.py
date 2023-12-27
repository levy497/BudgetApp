from sqlalchemy import DECIMAL
from __init__ import db
class Uzytkownik(db.Model):
    __tablename__ = 'uzytkownicy'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    haslo = db.Column(db.String, nullable=False)
    nick = db.Column(db.String)

class Transakcja(db.Model):
    __tablename__ = 'transakcje'
    id = db.Column(db.Integer, primary_key=True)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey('uzytkownicy.id'))
    kategoria_id = db.Column(db.Integer, db.ForeignKey('kategorie.id'))
    opis = db.Column(db.String)
    kwota = db.Column(db.DECIMAL(10, 2), nullable=False)
    data_transakcji = db.Column(db.Date, nullable=False)
    typ = db.Column(db.String, nullable=False)
class Kategoria(db.Model):
    __tablename__ = 'kategorie'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String, nullable=False, unique=True)  # Dodano unikalność nazwy
    typ = db.Column(db.String, nullable=False)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey('uzytkownicy.id'), nullable=False)

    # Dodano backref dla łatwiejszego dostępu z modelu Uzytkownik
    uzytkownik = db.relationship('Uzytkownik', backref=db.backref('kategorie', lazy=True))


class Budzet(db.Model):
    __tablename__ = 'budzety'
    id = db.Column(db.Integer, primary_key=True)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey('uzytkownicy.id'))
    kategoria_id = db.Column(db.Integer, db.ForeignKey('kategorie.id'))
    kwota = db.Column(DECIMAL(10, 2), nullable=False)
    miesiac = db.Column(db.Integer, nullable=False)
    rok = db.Column(db.Integer, nullable=False)