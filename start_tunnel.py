import subprocess
import requests
import time
import re

# Step 1: Start your Flask app
flask_process = subprocess.Popen(["python", "run.py"])

# Wait a bit for the server to start
time.sleep(3)

# Step 2: Start localtunnel
lt_process = subprocess.Popen(["lt", "--port", "5000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Step 3: Wait for the URL
url = None
for line in lt_process.stdout:
    print(line.strip())
    match = re.search(r'https://[a-z0-9\-]+\.loca\.lt', line)
    if match:
        url = match.group(0)
        print(f"✅ Tunnel active at: {url}")
        break

if not url:
    print("❌ Could not find LocalTunnel URL.")
    flask_process.kill()
    lt_process.kill()
    exit(1)

# Step 4: Update your frontend (example below)
frontend_repo_url = "https://api.vercel.com/v1/projects/YOUR_PROJECT_ID/env/FRONTEND_API_URL"
token = "YOUR_VERCEL_API_TOKEN"

response = requests.patch(
    frontend_repo_url,
    headers={"Authorization": f"Bearer {token}"},
    json={"value": url + "/api"}
)

if response.status_code == 200:
    print("✅ Frontend environment updated successfully!")
else:
    print(f"⚠️ Failed to update frontend: {response.text}")

# Keep running
flask_process.wait()
