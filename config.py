import os
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load secrets from .env or use defaults
ACCESS_SECRET = os.getenv("ACCESS_SECRET", "default_access_secret")
REFRESH_SECRET = os.getenv("REFRESH_SECRET", "default_refresh_secret")

