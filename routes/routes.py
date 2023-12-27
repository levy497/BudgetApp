from flask import Blueprint, request, jsonify
from services.auth_controller import AuthController
from services.budzet_controller import BudgetController
from services.kategorie_controller import KategorieController
from services.transakcje_controller import TransakcjeController
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token

# Tworzenie blueprintów
auth_bp = Blueprint('auth_bp', __name__)
transakcje_bp = Blueprint('transakcje_bp', __name__)
kategorie_bp = Blueprint('kategorie_bp', __name__)
budget_bp = Blueprint('budget', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return AuthController.login(data)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result = AuthController.register(data['email'], data['password'], data['nick'])
    return jsonify(result)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout successful"})

@transakcje_bp.route('/add-wydatek', methods=['POST'])
@jwt_required()
def add_wydatek():
    return TransakcjeController.add_wydatek()


@transakcje_bp.route('/get-wydatki', methods=['GET'])
@jwt_required()
def get_wydatki():
    current_user_id = get_jwt_identity()['id']
    result = TransakcjeController.get_wydatki(current_user_id)
    return jsonify(result)


@kategorie_bp.route('/get-kategorie', methods=['GET'])
@jwt_required()
def get_kategorie():
    return KategorieController.get_kategorie()


@kategorie_bp.route('/add-kategoria', methods=['POST'])
@jwt_required()
def add_kategoria():
    data = request.get_json()
    return KategorieController.add_kategoria(data)


@auth_bp.route('/status', methods=['GET'])
@jwt_required()
def user_status():
    return AuthController.status()

@budget_bp.route('/get-budget', methods=['GET'])
@jwt_required()
def get_budget():
    return BudgetController.get_budget()

@transakcje_bp.route('/delete-wydatek/<int:id>', methods=['DELETE'])
def delete_wydatek(id):
    return TransakcjeController.delete_wydatek(id)