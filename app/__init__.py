from datetime import timedelta  # ✅ add this import

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os
import psycopg2
from dotenv import load_dotenv

# --- Load environment variables from .env ---
load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # --- Get DATABASE_URL from environment ---
    db_url = os.getenv("DATABASE_URL")

    # --- Debugging Log ---
    print("🔍 Checking DATABASE_URL environment variable...")
    if db_url:
        print(f"✅ DATABASE_URL found: {db_url}")
    else:
        print("❌ DATABASE_URL is missing! Flask will not start.")
        raise RuntimeError("DATABASE_URL not set in environment variables.")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        print("ℹ️ Converted old postgres:// to postgresql://")

    try:
        print("🧩 Testing database connection...")
        conn = psycopg2.connect(db_url)
        conn.close()
        print("✅ PostgreSQL connection successful.")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        raise RuntimeError("Database connection failed.")

    # --- Flask Config ---
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")

    # ✅ JWT Expiration Settings
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)  # logged in for 12 hours
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # refresh valid for 30 days

    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # --- CORS Configuration ---
    CORS(app,
         resources={r"/api/*": {
             "origins": [
                 "https://ai-crop-disease-frontend.vercel.app",
                 "https://*.app.github.dev",
                 "http://localhost:3000",
                 "http://localhost:4200"
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})

    # --- Register Blueprints ---
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    with app.app_context():
        db.create_all()
        print("🗂️ All tables created or already exist.")

    print("🚀 Flask app initialized successfully and ready to serve.")
    return app
