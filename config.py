import os
from dotenv import load_dotenv

load_dotenv()

# Настройки базы данных MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           
    'password': 'password',   
    'database': 'scissors_bar'
}

# JWT настройки
JWT_SECRET = "scissors_bar_super_secret_key_2026"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
