from dotenv import load_dotenv
import os


load_dotenv()

AFFERENS_API_KEY = os.getenv("AFFERENS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if AFFERENS_API_KEY is None:
    raise ValueError("AFFERENS_API_KEY missing from .env")

if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY missing from .env")

print("Config loaded successfully")
