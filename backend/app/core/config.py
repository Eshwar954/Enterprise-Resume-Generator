from os import getenv

from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
GEMINI_API=getenv("GEMINI_API_KEY")
GROQ_API=getenv("GROQ_API_KEY")
