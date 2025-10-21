import sys
import os

# Ensure Python can find your app package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway provides PORT dynamically
    app.run(host="0.0.0.0", port=port)
