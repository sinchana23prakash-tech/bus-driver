import os
from pathlib import Path
from dotenv import load_dotenv

# Load root .env
BASE_DIR = Path(__file__).resolve().parent
ROOT_ENV_PATH = BASE_DIR.parent / '.env'
if ROOT_ENV_PATH.exists():
    load_dotenv(ROOT_ENV_PATH)
else:
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college-fuel-management-secure-secret-key-2026-v1')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-college-fuel-auth-token-super-secure-key-2026')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours
    
    # Uploads directory (stored safely outside web root)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'bills')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}
    
    # Governance Policies
    VC_CAN_APPROVE = os.environ.get('VC_CAN_APPROVE', 'false').lower() in ('true', '1', 't')
    
    # OCR & Duplicate Settings
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    IMAGE_HASH_HAMMING_THRESHOLD = int(os.environ.get('IMAGE_HASH_HAMMING_THRESHOLD', 6))
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'college_bus_fuel_db')
    
    # Fallback SQLite path
    SQLITE_PATH = os.path.join(BASE_DIR, 'college_bus_fuel.db')
    
    @classmethod
    def get_database_uri(cls):
        # If MySQL password or user is specified, attempt MySQL connection string
        # If password is empty or MySQL connection is refused, SQLite is used automatically
        if cls.MYSQL_USER and cls.MYSQL_PASSWORD:
            return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}?charset=utf8mb4"
        return f"sqlite:///{cls.SQLITE_PATH}"

class TestConfig(Config):
    TESTING = True
    SQLITE_PATH = os.path.join(BASE_DIR, 'test_college_bus_fuel.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    JWT_ACCESS_TOKEN_EXPIRES = 3600
