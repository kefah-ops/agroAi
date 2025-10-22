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

    # --- Use DATABASE_URL (works for Docker and Railway) ---
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise RuntimeError("❌ DATABASE_URL not set. Please add it to your environment variables.")

    # Fix for old-style postgres:// URLs
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")

    # --- Initialize extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Register routes ---
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # --- Health check route ---
    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    # --- Safe DB connection test (no crash if DB not ready yet) ---
    @app.before_request
    def check_db_connection():
        try:
            db.session.execute("SELECT 1")
        except Exception as e:
            print("⚠️ Database not ready:", e)

    return app
