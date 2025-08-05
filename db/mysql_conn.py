import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect(user='user', password='pass', database='spotify')