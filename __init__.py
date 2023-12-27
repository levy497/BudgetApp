from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS
import os
db = SQLAlchemy()  # Inicjalizacja db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    jwt = JWTManager(app)

    db.init_app(app)
    # Konfiguracja JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']


    with app.app_context():
        from routes import routes  # Import wewnątrz kontekstu aplikacji
        #db.create_all()
        app.register_blueprint(routes.auth_bp)
        app.register_blueprint(routes.transakcje_bp)
        app.register_blueprint(routes.kategorie_bp)
        app.register_blueprint(routes.budget_bp)

        db.create_all()

    return app
