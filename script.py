# Libraries
import sys
import csv
import json
import datetime
import mysql.connector
import logging
#Variables
artist_input_to_clean = '/home/dans/Documents/Uni/DM_project/mysql/init/artists.csv'
artist_output_cleaned = '/home/dans/Documents/Uni/DM_project/mysql/init/artists_clean.csv'

tracks_input_to_clean = '/home/dans/Documents/Uni/DM_project/mysql/init/tracks.csv'
tracks_output_cleaned = '/home/dans/Documents/Uni/DM_project/mysql/init/tracks_clean.csv'

conn = mysql.connector.connect(user='user', password='pass', database='spotify')
cur = conn.cursor()

#Cleaning Functions
#   Clean Artist
#   Clean Tracks

def clean_artist():
    with open(artist_input_to_clean, newline='', encoding='utf-8') as infile, open(artist_output_cleaned, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            # Gestione colonna followers mancante o vuota
            if not row.get('followers') or row['followers'].strip() == '':
                row['followers'] = '0'

            raw_genres = row['genres'].strip()
            try:
                # Caso ideale: è già JSON valido
                genres = json.loads(raw_genres)
            except:
                # Prova a trasformarlo in array (es. da "pop,rock" → ["pop", "rock"])
                if raw_genres.startswith('[') and raw_genres.endswith(']'):
                    genres = [g.strip().strip('"').strip("'") for g in raw_genres[1:-1].split(',') if g.strip()]
                elif raw_genres:
                    genres = [raw_genres.strip()]
                else:
                    genres = []

            row['genres'] = json.dumps(genres)
            writer.writerow(row)

def clean_tracks():
    with open(tracks_input_to_clean, newline='', encoding='utf-8') as infile, open(tracks_output_cleaned, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            for field in ['artists', 'id_artists']:
                raw = row[field].strip()
                try:
                    parsed = json.loads(raw)
                except:
                    # Se sembra una lista (es. [a, b]), prova a ripulirla
                    if raw.startswith('[') and raw.endswith(']'):
                        parsed = [g.strip().strip('"').strip("'") for g in raw[1:-1].split(',') if g.strip()]
                    elif raw:
                        parsed = [raw.strip()]
                    else:
                        parsed = []
                row[field] = json.dumps(parsed)

            writer.writerow(row)

#Load functions
#   Load Artist
#   Load Tracks

def load():
    with open(artist_output_cleaned, newline='', encoding='utf-8') as infile:
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
    with open(tracks_output_cleaned, newline='', encoding='utf-8') as infile:
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
                release_date_raw = row['release_date'].strip()
                print(f"TRACK {row['id']} — release_date raw: {release_date_raw}")
                
                if len(release_date_raw) == 10:
                    try:
                        release_date = datetime.datetime.strptime(release_date_raw, '%Y-%m-%d').date()
                    except ValueError:
                        release_date = datetime.date(1900, 1, 1)
                        print(f"[WARN] TRACK {row['id']}: release_date non valida ({release_date_raw}). Uso data di default {release_date}")
                elif len(release_date_raw) == 7:
                    # Caso in cui è presente solo anno e mese, es. "YYYY-MM"
                    try:
                        year, month = release_date_raw.split('-')
                        release_date = datetime.date(int(year), int(month), 1)
                        print(f"[INFO] TRACK {row['id']}: release_date impostata a {release_date} (anno e mese presenti)")
                    except Exception as e:
                        release_date = datetime.date(1900, 1, 1)
                        print(f"[WARN] TRACK {row['id']}: formato release_date non valido ({release_date_raw}). Uso data di default {release_date}. Errore: {e}")
                elif len(release_date_raw) == 4 and release_date_raw.isdigit():
                    release_date = datetime.date(int(release_date_raw), 1, 1)
                    print(f"[INFO] TRACK {row['id']}: release_date impostata a {release_date} (solo anno presente)")
                else:
                    release_date = datetime.date(1900, 1, 1)
                    print(f"[WARN] TRACK {row['id']}: release_date incompleta ({release_date_raw}). Uso data di default {release_date}")

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
                    str(release_date),
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


#clean_artist()
#clean_tracks()
load()