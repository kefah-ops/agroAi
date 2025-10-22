from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os
import psycopg2
from dotenv import load_dotenv  # ✅ Added this line

# --- Load environment variables from .env ---
load_dotenv()  # ✅ This ensures DATABASE_URL and JWT_SECRET_KEY are loaded

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

    # --- Convert old postgres:// URL if necessary ---
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        print("ℹ️ Converted old postgres:// to postgresql://")

    # --- Test PostgreSQL connection before starting ---
    try:
        print("🧩 Testing database connection...")
        conn = psycopg2.connect(db_url)
        conn.close()
        print("✅ PostgreSQL connection successful.")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        raise RuntimeError("Database connection failed. Check DATABASE_URL or Railway settings.")

    # --- Flask Config ---
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")

    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    frontend_url = "https://ai-crop-disease-frontend.vercel.app"
    CORS(app, resources={r"/api/*": {"origins": frontend_url}}, supports_credentials=True)


    # --- Register Blueprints ---
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # --- Health Check Route ---
    @app.route("/api/health")
    def health():
        return {"status": "ok"}, 200

    # --- Create Tables ---
    with app.app_context():
        db.create_all()
        print("🗂️ All tables created or already exist.")

    print("🚀 Flask app initialized successfully and ready to serve.")
    return app
