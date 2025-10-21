from app import db

class UploadedImage(db.Model):
    __tablename__ = 'uploaded_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())

    # ✅ Foreign key to users.id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship
    user = db.relationship('User', back_populates='images')
    diagnosis = db.relationship('AIDiagnosis', back_populates='image', uselist=False)

    def __repr__(self):
        return f"<UploadedImage {self.filename}>"
