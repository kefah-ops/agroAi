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


# --- Diagnose Endpoint ---
@ai_bp.route('/diagnose', methods=['POST', 'OPTIONS'])
@jwt_required()
def diagnose():
    """Image diagnosis endpoint using Gemini AI"""
    
    print(f"📨 Received {request.method} request to /diagnose")
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'image' not in request.files:
        print("❌ No image in request")
        return jsonify({"error": "Image file is required"}), 400

    try:
        current_user_id = get_jwt_identity()
        print(f"✅ Authenticated user: {current_user_id}")
        
        image = request.files['image']
        print(f"📷 Processing image: {image.filename}")
        
        # Use the correct model name
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

        # Improved prompt for structured response
        prompt = """Analyze this crop/plant image and provide a detailed diagnosis.

Please format your response as follows:
- Disease/Condition: [Name of the disease or state "Healthy" if no issues]
- Confidence Level: [High/Medium/Low]
- Symptoms Observed: [List visible symptoms]
- Recommended Actions: [Specific treatment or preventive measures]

Be specific and practical in your recommendations."""

        # Read image data
        image_data = image.read()
        
        response = model.generate_content([
            prompt,
            {"mime_type": image.mimetype, "data": image_data}
        ])

        # Extract text from response
        diagnosis_text = getattr(response, "text", None)
        if not diagnosis_text and hasattr(response, "candidates"):
            diagnosis_text = response.candidates[0].content.parts[0].text
        diagnosis_text = diagnosis_text or "No diagnosis generated."
        
        print(f"🔬 Gemini response: {diagnosis_text[:200]}...")

        # Parse the response to extract structured data
        parsed_result = parse_gemini_response(diagnosis_text)
        
        # Return both structured data and full text
        response_data = {
            "disease": parsed_result.get("disease", "Unknown"),
            "confidence": parsed_result.get("confidence", 0.5),
            "recommendation": parsed_result.get("recommendation", diagnosis_text),
            "full_diagnosis": diagnosis_text  # Include full text as well
        }
        
        print(f"✅ Sending response: {response_data}")
        
        return jsonify(response_data), 200

    except Exception as e:
        print(f"❌ Diagnosis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def parse_gemini_response(text):
    """
    Parse Gemini's text response to extract structured data
    """
    result = {
        "disease": "Unknown",
        "confidence": 0.5,
        "recommendation": text
    }
    
    try:
        # Extract disease/condition
        disease_match = re.search(r'Disease/Condition:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if disease_match:
            result["disease"] = disease_match.group(1).strip()
        
        # Extract confidence level and convert to number
        confidence_match = re.search(r'Confidence Level:\s*(\w+)', text, re.IGNORECASE)
        if confidence_match:
            confidence_level = confidence_match.group(1).lower()
            if 'high' in confidence_level:
                result["confidence"] = 0.9
            elif 'medium' in confidence_level:
                result["confidence"] = 0.7
            elif 'low' in confidence_level:
                result["confidence"] = 0.5
        
        # Extract recommendation
        recommendation_match = re.search(r'Recommended Actions:\s*(.+?)(?:\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if recommendation_match:
            result["recommendation"] = recommendation_match.group(1).strip()
        else:
            # If can't find "Recommended Actions", try to extract everything after "Symptoms"
            recommendation_match = re.search(r'Symptoms Observed:.*?\n(.+)', text, re.IGNORECASE | re.DOTALL)
            if recommendation_match:
                result["recommendation"] = recommendation_match.group(1).strip()
        
    except Exception as e:
        print(f"⚠️ Error parsing response: {e}")
    
    return result