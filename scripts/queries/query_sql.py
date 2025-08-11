import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mysql_conn import get_mysql_connection

conn = get_mysql_connection()
cur = conn.cursor()

cur.execute("SELECT * FROM tracks WHERE name = 'Let It Be'")
results = cur.fetchall()
for row in results:
    print(row)



# Seconda query
cur.execute("SELECT popularity, loudness  FROM tracks ORDER BY loudness ASC")
results = cur.fetchall()
print("\nTracce meno popolari:")
for row in results:
    print(row)

cur.close()
conn.close()