import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
SERVER_URL = os.environ.get("SERVER_URL", "http://g4.etsisi.upm.es:8833/v1")
MODEL_ID = os.environ.get("MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
