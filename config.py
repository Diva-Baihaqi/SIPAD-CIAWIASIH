from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'sid_desa'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306) # Wajib untuk Aiven
    MYSQL_CURSORCLASS = 'DictCursor' # Agar hasil query berupa Dictionary
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
