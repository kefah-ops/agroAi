from app import create_app, db
from app.models.user_model import User
from app.models.uploaded_image_model import UploadedImage
from app.models.ai_diagnosis_model import AIDiagnosis
from app.models.chat_log_model import ChatLog
from app.models.disease_info_model import DiseaseInfo

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ All tables created successfully!")
