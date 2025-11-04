from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import google.generativeai as genai
import os
from auth_optional import optional_jwt  # ✅ import optional decorator

ai_bp = Blueprint("ai_bp", __name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
FREE_MODEL = "models/gemini-2.5-flash"

@ai_bp.route("/models", methods=["GET"])
@optional_jwt
def list_models():
    try:
        models = genai.list_models()
        model_info = [{"name": getattr(m, "name", None)} for m in models]
        return jsonify({"models": model_info}), 200

    except Exception as e:
        print("❌ LIST MODELS ERROR:", e)
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/chat", methods=["POST"])
@optional_jwt  # ✅ allows both guests and logged-in users
def chat():
    try:
        user = get_jwt_identity()  # None if guest
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "Message required"}), 400

        model = genai.GenerativeModel(FREE_MODEL)
        response = model.generate_content(
            f"You are AgroAI. Help farmers.\nUser({user}): {message}"
        )

        return jsonify({"response": response.text}), 200

    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/diagnose", methods=["POST"])
@optional_jwt
def diagnose():
    try:
        file = request.files.get("image") or request.files.get("file")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        filepath = f"/tmp/{file.filename}"
        file.save(filepath)

        with open(filepath, "rb") as img:
            img_data = img.read()

        model = genai.GenerativeModel(FREE_MODEL)

        response = model.generate_content([
            "Analyze plant leaf disease, confidence %, and provide treatment steps.",
            {"mime_type": file.content_type, "data": img_data}
        ])

        os.remove(filepath)

        return jsonify({"diagnosis": response.text}), 200

    except Exception as e:
        print("❌ DIAG ERROR:", e)
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500
