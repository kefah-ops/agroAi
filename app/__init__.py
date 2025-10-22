from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# --- Initialize extensions ---
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    # --- Load environment variables safely ---
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)

    app = Flask(__name__)

    # --- Database Configuration ---
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise RuntimeError("❌ DATABASE_URL is missing! Please set it in your .env or Railway Variables.")

    # Fix for older postgres:// URLs
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")

    # --- Initialize Flask extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Register Blueprints ---
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # --- Optional Health Check (for deployment debugging) ---
    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    # --- Initialize Database Tables ---
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully.")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

    return app
