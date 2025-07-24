import csv
import json
import mysql.connector

conn = mysql.connector.connect(user='user', password='pass', database='spotify')
cur = conn.cursor()

with open('/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/artists_clean.csv', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        try:
            # Tenta di interpretare genres come JSON
            genres = json.loads(row['genres'])
        except Exception as e:
            print(f"[WARN] Riga con ID {row['id']}: genres non valido ({row['genres']}). Uso array vuoto. Errore: {e}")
            genres = []

        try:
            cur.execute("""
                INSERT IGNORE INTO artists (id, followers, genres, name, popularity)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row['id'],
                int(float(row['followers'])),
                json.dumps(genres),
                row['name'],
                int(row['popularity'])
            ))
        except Exception as e:
            print(f"[ERROR] Riga con ID {row['id']}: errore durante INSERT — {e}")

conn.commit()
cur.close()
conn.close()