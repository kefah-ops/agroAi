import sys
import os

# Ensure Python can find your app package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db  # ✅ Correct import

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
