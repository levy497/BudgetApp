from datetime import datetime
import decimal

from flask import Flask, jsonify, request, make_response, session
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import DECIMAL
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Konfiguracja bazy danych
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://levy497:ewnewejn#EDS1@bazadanych.postgres.database.azure.com:5432/budget_app'
db = SQLAlchemy(app)

# Konfiguracja JWT
app.config['JWT_SECRET_KEY'] = 'SDDCDDE2wesdnew90kwek2##dssjndskd'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)

# Model użytkownika zgodny z tabelą w SQLAlchemy
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
# with app.app_context():
#
#     db.create_all()
# Endpoint logowania
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)


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

# Endpoint rejestracji
@app.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    nick = request.json.get('nick', None)

    if not email or not password or not nick:
        return jsonify({"msg": "Missing email, password or nick"}), 400

    user = Uzytkownik.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "Email already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = Uzytkownik(email=email, haslo=hashed_password, nick=nick)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(msg="User created successfully"), 201

# Endpoint sprawdzania statusu użytkownika
@app.route('/status', methods=['GET'])
@jwt_required()
def user_status():
    current_user_email = get_jwt_identity()['email']
    user = Uzytkownik.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(logged_in_as=user.email, nick=user.nick), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_email = get_jwt_identity()['email']
    user = Uzytkownik.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Pobieranie danych o budżecie i transakcjach
    budzety = Budzet.query.filter_by(uzytkownik_id=user.id).all()
    transakcje = Transakcja.query.filter_by(uzytkownik_id=user.id).all()

    # Przygotowanie danych do wysłania
    budzety_data = [{"kwota": budzet.kwota, "miesiac": budzet.miesiac, "rok": budzet.rok} for budzet in budzety]
    transakcje_data = [
        {"opis": transakcja.opis, "kwota": transakcja.kwota, "data_transakcji": transakcja.data_transakcji} for
        transakcja in transakcje]

    return jsonify(nick=user.nick, budzety=budzety_data, transakcje=transakcje_data), 200

@app.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()['email']
    new_token = create_access_token(identity=current_user, expires_delta=datetime.timedelta(days=1))
    return jsonify(access_token=new_token), 200
# Endpoint wylogowania
@app.route('/logout', methods=['POST'])
def logout():
    return jsonify(msg="Logout successful"), 200


@app.route('/add-wydatek', methods=['POST'])
@jwt_required()
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

        kategoria = Kategoria.query.filter_by(id=kategoria_id).first()
        if not kategoria:
            return jsonify({"msg": "Kategoria not found"}), 404

        nowy_wydatek = Transakcja(
            uzytkownik_id=user.id,
            kategoria_id=kategoria_id,
            opis=opis,
            kwota=kwota,
            data_transakcji=data_transakcji,
            typ='wydatek'
        )
        db.session.add(nowy_wydatek)

        miesiac, rok = data_transakcji.month, data_transakcji.year
        budzet = Budzet.query.filter_by(
            uzytkownik_id=user.id,
            kategoria_id=kategoria_id,
            miesiac=miesiac,
            rok=rok
        ).first()

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

        return jsonify({"msg": "Wydatek dodany pomyślnie"}), 201

    except KeyError as e:
        return jsonify({"msg": "Brakujące dane", "error": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500

@app.route('/add-kategoria', methods=['POST'])
@jwt_required()
def add_kategoria():
    print("Dane żądania:", request.json)

    current_user_id = get_jwt_identity()['id']  # Pobierz ID zalogowanego użytkownika z tokena JWT
    print(request.json)
    data = request.get_json()
    nazwa = data.get('nazwa')
    typ = data.get('typ')

    if not nazwa or not typ:
        return jsonify({"message": "Brak nazwy lub typu kategorii"}), 400


    nowa_kategoria = Kategoria(nazwa=nazwa, typ=typ, uzytkownik_id=current_user_id)
    db.session.add(nowa_kategoria)
    db.session.commit()

    return jsonify({"message": "Kategoria dodana pomyślnie"}), 201


@app.route('/get-kategorie', methods=['GET'])
@jwt_required()
def get_kategorie():
    current_user_id = get_jwt_identity()["id"]
    kategorie = Kategoria.query.filter_by(uzytkownik_id=current_user_id).all()
    kategorie_data = [{"id": kategoria.id, "nazwa": kategoria.nazwa, "typ": kategoria.typ} for kategoria in kategorie]

    return jsonify(kategorie_data), 200
# @app.route('/get-wydatki', methods=['GET'])
# @jwt_required()
# def get_wydatki():
#     current_user_id = get_jwt_identity()["id"]
#     wydatki = Transakcja.query.filter_by(uzytkownik_id=current_user_id).all()
#     wydatek_data = ['']


if __name__ == '__main__':
    app.run(debug=True)