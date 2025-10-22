import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    DEBUG = True
    AI_MODEL_PATH = "models/my_model.pkl"  # or endpoint
    
    # Add PostgreSQL configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:kefah@db:5432/postgres'  # Default for local dev
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False