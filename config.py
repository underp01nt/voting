import dotenv, os

dotenv.load_dotenv()

class Configuration:
    SESSION_MIDDLEWARE_SECRET_KEY = os.getenv("SESSION_MIDDLEWARE_SECRET_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

settings = Configuration()