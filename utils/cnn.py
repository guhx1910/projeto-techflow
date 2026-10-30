import mysql.connector


def conectar():
    return mysql.connector.connect(
        host="172.16.78.112",
        port=3306,
        user="gustavo",
        password="gustavo123",
        database="db_techvarejo"
    )