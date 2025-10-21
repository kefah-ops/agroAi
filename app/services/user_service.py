from app.models.user_model import User

def get_all_users():
    users = User.query.all()
    return [{"username": u.username, "email": u.email} for u in users]
