from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
import os

ai_bp = Blueprint("ai_bp", __name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@ai_bp.route('/chat', methods=['POST', 'OPTIONS'])
@jwt_required()
def chat():
    """Unified AI endpoint for text and image input using Gemini"""
    
    # --- Handle CORS preflight ---
    if request.method == 'OPTIONS':
        return '', 200

    try:
        current_user_id = get_jwt_identity()
        print(f"✅ Authenticated user: {current_user_id}")

        # --- Handle text or image ---
        if request.content_type.startswith('multipart/form-data'):
            # User uploaded an image
            file = request.files.get('image')
            if not file:
                return jsonify({"error": "No image file provided"}), 400

            # Save temporarily
            filepath = f"/tmp/{file.filename}"
            file.save(filepath)

            print(f"🖼️ Received image: {file.filename}")

            # Use Gemini vision model
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                "You are AgroAI, an expert crop health assistant. Analyze this image of a plant leaf and detect if it has any disease. Include disease name, confidence level, and farming recommendations.",
                {"mime_type": "image/jpeg", "data": open(filepath, "rb").read()}
            ])

            diagnosis_text = getattr(response, "text", None)
            if not diagnosis_text and hasattr(response, "candidates"):
                diagnosis_text = response.candidates[0].content.parts[0].text
            diagnosis_text = diagnosis_text or "No diagnosis available."

            print(f"🧠 AI Diagnosis: {diagnosis_text[:120]}...")
            return jsonify({
                "type": "image_analysis",
                "response": diagnosis_text
            }), 200

        else:
            # Handle normal chat messages
            data = request.get_json()
            query = data.get('message')
            if not query:
                return jsonify({"error": "No message provided"}), 400

            print(f"💬 Text message: {query}")

            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            prompt = f"""
You are AgroAI, an expert agricultural assistant specializing in crop health and farming advice.

User: {query}

Provide a helpful, practical, and accurate farming response.
"""
            response = model.generate_content(prompt)

            response_text = getattr(response, "text", None)
            if not response_text and hasattr(response, "candidates"):
                response_text = response.candidates[0].content.parts[0].text
            response_text = response_text or "I couldn't generate a response. Please try again."

            print(f"🤖 AI Response: {response_text[:100]}...")
            return jsonify({
                "type": "text_chat",
                "response": response_text
            }), 200

    except Exception as e:
        print(f"❌ AI Route Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
