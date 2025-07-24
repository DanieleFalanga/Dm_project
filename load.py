import csv
import json
import mysql.connector

conn = mysql.connector.connect(user='user', password='pass', database='spotify')
cur = conn.cursor()

with open('/home/dans/Documents/Uni/DM_project/mysql/init/artists_clean.csv', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        try:
            genres = json.loads(row['genres'])
        except Exception as e:
            print(f"[WARN] ARTIST {row['id']}: genres non valido ({row['genres']}). Uso array vuoto. Errore: {e}")
            genres = []

        try:
            cur.execute("""
                INSERT IGNORE INTO artists (id, followers, genres, name, popularity)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row['id'],
                int(row['followers'].split('.')[0]),
                json.dumps(genres),
                row['name'],
                int(row['popularity'])
            ))
        except Exception as e:
            print(f"[ERROR] ARTIST {row['id']}: errore INSERT — {e}")

# -------------------- Caricamento TRACKS --------------------
with open('/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/tracks_clean.csv', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        try:
            artists = json.loads(row['artists'])
        except Exception as e:
            print(f"[WARN] TRACK {row['id']}: artists non valido ({row['artists']}). Uso array vuoto. Errore: {e}")
            artists = []

        try:
            id_artists = json.loads(row['id_artists'])
        except Exception as e:
            print(f"[WARN] TRACK {row['id']}: id_artists non valido ({row['id_artists']}). Uso array vuoto. Errore: {e}")
            id_artists = []

        try:
            # parsing della data (in caso sia vuota o malformata)
            try:
                release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
            except:
                release_date = None

            cur.execute("""
                INSERT IGNORE INTO tracks (
                    id, name, popularity, duration_ms, explicit,
                    artists, id_artists, release_date,
                    danceability, energy, `key`, loudness,
                    mode, speechiness, acousticness,
                    instrumentalness, liveness, valence,
                    tempo, time_signature
                ) VALUES (%s, %s, %s, %s, %s,
                          %s, %s, %s,
                          %s, %s, %s, %s,
                          %s, %s, %s,
                          %s, %s, %s,
                          %s, %s)
            """, (
                row['id'],
                row['name'],
                int(row['popularity']),
                int(row['duration_ms']),
                int(row['explicit']),
                json.dumps(artists),
                json.dumps(id_artists),
                release_date,
                float(row['danceability']),
                float(row['energy']),
                int(row['key']),
                float(row['loudness']),
                int(row['mode']),
                float(row['speechiness']),
                float(row['acousticness']),
                float(row['instrumentalness']),
                float(row['liveness']),
                float(row['valence']),
                float(row['tempo']),
                int(row['time_signature'])
            ))
        except Exception as e:
            print(f"[ERROR] TRACK {row['id']}: errore INSERT — {e}")

# -------------------- Chiusura connessione --------------------
conn.commit()
cur.close()
conn.close()