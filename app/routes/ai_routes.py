from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
import os
from PIL import Image

ai_bp = Blueprint('ai_bp', __name__)

# Configure Gemini API globally
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Chat Endpoint ---
@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # ✅ Correct model reference
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")

        # Generate the AI's response
        response = model.generate_content(user_message)

        ai_reply = response.text
        user = get_jwt_identity()

        return jsonify({
            "user": user,
            "user_message": user_message,
            "response": ai_reply
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Diagnose Endpoint ---
@ai_bp.route('/diagnose', methods=['POST'])
@jwt_required()
def diagnose():
    if 'image' not in request.files:
        return jsonify({"error": "Image file is required"}), 400

    try:
        image = request.files['image']
        image_path = f"temp_{image.filename}"
        image.save(image_path)

        img = Image.open(image_path)
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")

        prompt = "Analyze this crop image and describe any possible diseases or visible issues."

        response = model.generate_content([prompt, img])
        diagnosis_text = response.text or "No diagnosis generated."

        return jsonify({"diagnosis": diagnosis_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
