from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Priority: Standard env vars (e.g. from .env) -> Railway automatic env vars -> Default localhost fallback
    
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or os.environ.get('MYSQLHOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or os.environ.get('MYSQLUSER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or os.environ.get('MYSQLPASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or os.environ.get('MYSQLDATABASE') or 'sid_desa'
    
    # Port handling logic
    _port = os.environ.get('MYSQL_PORT') or os.environ.get('MYSQLPORT') or 3306
    try:
        MYSQL_PORT = int(_port)
    except ValueError:
        MYSQL_PORT = 3306
        
    MYSQL_CURSORCLASS = 'DictCursor' # Agar hasil query berupa Dictionary
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
