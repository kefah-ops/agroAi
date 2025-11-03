from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
import os

ai_bp = Blueprint("ai_bp", __name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

FREE_MODEL = "models/gemini-2.5-flash"

@ai_bp.route("/models", methods=["GET"])
@jwt_required()
def list_models():
    try:
        models = genai.list_models()

        model_info = []
        for m in models:
            model_info.append({
                "name": getattr(m, "name", None)
            })

        return jsonify({"models": model_info}), 200

    except Exception as e:
        print("❌ LIST MODELS ERROR:", e)
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    try:
        user = get_jwt_identity()
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Message required"}), 400

        model = genai.GenerativeModel(FREE_MODEL)
        response = model.generate_content(
            f"You are AgroAI. Help farmers.\nUser: {message}"
        )

        return jsonify({ "response": response.text }), 200

    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/diagnose", methods=["POST"])
@jwt_required()
def diagnose():
    try:
        user = get_jwt_identity()

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        filepath = f"/tmp/{file.filename}"
        file.save(filepath)

        model = genai.GenerativeModel(FREE_MODEL)
        
        with open(filepath, "rb") as img:
            img_data = img.read()

        response = model.generate_content([
            "Analyze crop disease, confidence and treatment.",
            {"mime_type": "image/jpeg", "data": img_data}
        ])

        os.remove(filepath)

        return jsonify({ "diagnosis": response.text }), 200

    except Exception as e:
        print("❌ DIAG ERROR:", e)
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500
