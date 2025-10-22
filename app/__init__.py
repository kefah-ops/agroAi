from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # --- Database Configuration ---
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("❌ DATABASE_URL not set in environment variables!")

    # Fix deprecated postgres:// URIs
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Always require SSL in production
    if "sslmode" not in db_url:
        db_url += "?sslmode=require"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")

    # --- Initialize extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Register blueprints ---
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    with app.app_context():
        db.create_all()
        print("✅ Connected to PostgreSQL and tables created successfully")

    return app
