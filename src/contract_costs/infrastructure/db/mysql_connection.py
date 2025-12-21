import mysql.connector
from contract_costs.config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
