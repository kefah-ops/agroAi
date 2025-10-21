def generate_ai_response(message: str) -> str:
    """
    Example AI logic — later you can replace this with OpenAI API, Hugging Face, or your own model.
    """
    if not message:
        return "Please enter a message."

    lower_msg = message.lower()
    if "hello" in lower_msg:
        return "Hi there 👋! I'm AgroAI — how can I assist you today?"
    elif "crop" in lower_msg:
        return "I can help diagnose crop diseases. Please upload an image or describe the issue."
    elif "weather" in lower_msg:
        return "Today's weather looks great for planting 🌱."
    else:
        return "I'm your AI assistant, still learning to understand you better!"
