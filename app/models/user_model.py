from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'  # 👈 properly indented

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text)

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
