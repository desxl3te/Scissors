import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

# Создаем пул соединений для Master (запись)
master_pool = pooling.MySQLConnectionPool(
    pool_name="master_pool",
    pool_size=5,
    **DB_CONFIG
)

# Создаем пул соединений для Slave (чтение)

slave_pool = pooling.MySQLConnectionPool(
    pool_name="slave_pool",
    pool_size=5,
    **DB_CONFIG
)

def get_master_connection():
    
    return master_pool.get_connection()

def get_slave_connection():
    
    return slave_pool.get_connection()
