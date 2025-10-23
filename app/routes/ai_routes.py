from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
import os
import re  # ✅ ADD THIS IMPORT

ai_bp = Blueprint('ai_bp', __name__)

# Configure Gemini API globally
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# --- Chat Endpoint ---
@ai_bp.route('/chat', methods=['POST', 'OPTIONS'])
@jwt_required()
def chat():
    """Chat endpoint using Gemini AI"""
    
    print(f"📨 Received {request.method} request to /chat")
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        current_user_id = get_jwt_identity()
        print(f"✅ Authenticated user: {current_user_id}")
        
        data = request.get_json()
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        print(f"💬 User message: {user_message}")
        
        # Use Gemini for chat
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        prompt = f"""You are AgroAI, an expert agricultural assistant specializing in crop health and farming advice.
        
User question: {user_message}

Provide a helpful, practical response focused on agriculture and crop management."""

        response = model.generate_content(prompt)
        
        # Extract response text
        response_text = getattr(response, "text", None)
        if not response_text and hasattr(response, "candidates"):
            response_text = response.candidates[0].content.parts[0].text
        response_text = response_text or "I couldn't generate a response. Please try again."
        
        print(f"🤖 AI response: {response_text[:100]}...")
        
        return jsonify({
            "user": current_user_id,
            "user_message": user_message,
            "response": response_text
        }), 200
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@ai_bp.route('/diagnose', methods=['POST', 'OPTIONS'])
@jwt_required()
def diagnose():
    """Diagnose image using Gemini AI (JSON Enforced)"""
    
    print(f"📨 Received {request.method} request to /diagnose")

    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200

    if 'image' not in request.files:
        print("❌ No image file in request")
        return jsonify({"error": "Image file is required"}), 400

    try:
        current_user_id = get_jwt_identity()
        print(f"✅ Authenticated user: {current_user_id}")

        image = request.files['image']
        print(f"📷 Processing image: {image.filename}")

        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

        # ✅ Enforce JSON output
        prompt = """
        You are an expert plant pathologist AI. 
        Analyze the provided image and return ONLY a valid JSON object in this format:
        {
          "disease": "Disease name or 'Healthy'",
          "confidence": 0.0 to 1.0,
          "recommendation": "Actionable treatment or prevention advice"
        }

        Do NOT include any explanation or text outside the JSON.
        """

        image_data = image.read()
        response = model.generate_content([
            prompt,
            {"mime_type": image.mimetype, "data": image_data}
        ])

        # Extract raw Gemini text
        diagnosis_text = getattr(response, "text", None)
        if not diagnosis_text and hasattr(response, "candidates"):
            diagnosis_text = response.candidates[0].content.parts[0].text
        diagnosis_text = diagnosis_text.strip() if diagnosis_text else "{}"

        print(f"🔬 Gemini Raw Output: {diagnosis_text}")

        # ✅ Try parsing as JSON
        import json
        try:
            diagnosis_json = json.loads(diagnosis_text)
        except json.JSONDecodeError:
            print("⚠️ Gemini did not return valid JSON, fallback to manual parsing")
            diagnosis_json = {
                "disease": "Unknown",
                "confidence": 0.0,
                "recommendation": diagnosis_text
            }

        print(f"✅ Parsed Diagnosis: {diagnosis_json}")

        return jsonify(diagnosis_json), 200

    except Exception as e:
        print(f"❌ Diagnosis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
