import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    DEBUG = True
    AI_MODEL_PATH = "models/my_model.pkl"  # or endpoint
