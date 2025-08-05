import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mysql_conn import get_mysql_connection

conn = get_mysql_connection()
cur = conn.cursor()
cur.execute("""
    SELECT a.name,t.popularity 
    FROM artists a
    INNER JOIN tracks t ON a.name = t.name
       WHERE artists LIKE %s
    ORDER BY t.popularity ASC
""", ('%The Beatles%',))

results = cur.fetchall()
for row in results:
    print(row)


cur.close()
conn.close()