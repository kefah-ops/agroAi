from flask import Blueprint, request, jsonify
from app import db
from app.models.user_model import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

# -------------------------
# 🧩 Register User
# -------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create and save new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# -------------------------
# 🔐 Login User
# -------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate JWT access token
    access_token = create_access_token(identity=user.email)

    return jsonify({
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


# -------------------------
# 👤 Get User Profile (Protected)
# -------------------------
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200


# -------------------------
# ✏️ Update User Profile (Protected)
# -------------------------
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Update fields if provided
    if username:
        user.username = username
    if email:
        # Prevent duplicate email use
        if User.query.filter(User.email == email, User.id != user.id).first():
            return jsonify({"message": "Email already in use"}), 400
        user.email = email
    if password:
        user.set_password(password)

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200