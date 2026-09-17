import os

BASE_URL = os.getenv("BASE_URL", "https://automationintesting.online")
API_URL = f"{BASE_URL}/api"
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password")
HEADLESS = os.getenv("HEADLESS", "1") == "1"
