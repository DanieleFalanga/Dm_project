import mysql.connector
import time
import pandas as pd

dst_for_results = "/home/dans/Documents/Uni/DM_project/outputs/mySQL/"

run_num = 6

# Connessione a MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="user",
    password="pass",
    database="spotify"
)

mysql_cursor = mysql_conn.cursor(dictionary=True)

# Le query nominate in un dizionario
queries = {
    "Q1": """
        SELECT a.name,
           ROUND(AVG(CAST(t.popularity AS DECIMAL(10,2))), 2) AS avg_popularity,
           COUNT(*) AS n_tracks
        FROM spotify.tracks_artists ta
        JOIN tracks_info t ON t.id  = ta.track_id AND t.popularity IS NOT NULL
        JOIN artists a ON a.id = ta.artist_id
        GROUP BY a.id, a.name
        HAVING COUNT(*) >=60
        ORDER BY avg_popularity DESC
        LIMIT 20;
    """,
    "Q2": """
        SELECT tracks.name
        FROM tracks
        WHERE JSON_CONTAINS(tracks.artists, '"Eminem"') and JSON_LENGTH(tracks.artists) = 1
        ORDER BY tracks.popularity DESC LIMIT 50 
    """,
    "Q3": """
        WITH genre_stats AS (
          SELECT
            t.release_date,
            ga.genre,
            COUNT(*) AS track_count,
            AVG(t.popularity) AS avg_popularity
          FROM tracks_info AS t
          JOIN tracks_artists AS ta ON ta.track_id = t.id
          JOIN genres_artist AS ga ON ga.id = ta.artist_id
          GROUP BY t.release_date, ga.genre
        ),
        filtered AS (
          SELECT *
          FROM genre_stats
          WHERE track_count >= 200
        ),
        ranked AS (
          SELECT *,
                 ROW_NUMBER() OVER (PARTITION BY release_date ORDER BY avg_popularity DESC) AS rk
          FROM filtered
        )
        SELECT release_date, genre, avg_popularity, track_count
        FROM ranked
        WHERE rk = 1
        ORDER BY release_date;
    """
}

#Senza indici

# Struttura risultati per i tempi
execution_times = {qname: [] for qname in queries.keys()}

# Se vuoi salvare anche i risultati delle query (opzionale)
query_outputs = {qname: [] for qname in queries.keys()}

for qname, query in queries.items():
    for i in range(run_num):
        start_time = time.perf_counter()

        mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # ms

        print(f"{qname} - Run #{i+1} - Execution Time: {execution_time:.2f} ms")

        execution_times[qname].append(execution_time)
        query_outputs[qname].append(result)  # <-- salva output vero e proprio (se vuoi analizzarlo)

# DataFrame dei tempi
df_times = pd.DataFrame.from_dict(execution_times, orient="index", columns=[f"run_{i+1}" for i in range(run_num)])
print(df_times)

# Salvataggio
df_times.to_csv(dst_for_results + "Mysql_noIndex_times.csv")

# (opzionale) salvataggio dei risultati veri in un pickle
pd.to_pickle(query_outputs, dst_for_results + "Mysql_noIndex_outputs.pkl")


# Con Indexes

# Struttura risultati per i tempi
execution_times = {qname: [] for qname in queries.keys()}

# Se vuoi salvare anche i risultati delle query (opzionale)
query_outputs = {qname: [] for qname in queries.keys()}

# Inserire Indici qui 

indexes_sql = [
    "CREATE INDEX idx_genres_artist_id_genre ON genres_artist (id, genre);",
    "CREATE INDEX idx_tracks_artists_artist_id ON tracks_artists (artist_id);",
    "CREATE INDEX idx_tracks_artists_track_artist ON tracks_artists (track_id, artist_id);",
    "CREATE INDEX idx_tracks_info_id ON tracks_info (id);",
    "CREATE INDEX idx_tracks_info_release_date ON tracks_info (release_date);"
]

for index in indexes_sql:
    try:
        mysql_cursor.execute(index)
        print(f"Creato indice: {index}")
    except mysql.connector.Error as err:
        print(f"Errore su {index}: {err}")

for qname, query in queries.items():
    for i in range(run_num):
        start_time = time.perf_counter()

        mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # ms

        print(f"{qname} - Run #{i+1} - Execution Time: {execution_time:.2f} ms")

        execution_times[qname].append(execution_time)
        query_outputs[qname].append(result)  # <-- salva output vero e proprio (se vuoi analizzarlo)

# DataFrame dei tempi
df_times = pd.DataFrame.from_dict(execution_times, orient="index", columns=[f"run_{i+1}" for i in range(run_num)])
print(df_times)

# Salvataggio
df_times.to_csv(dst_for_results + "Mysql_withIndex_times.csv")

# (opzionale) salvataggio dei risultati veri in un pickle
pd.to_pickle(query_outputs, dst_for_results + "Mysql_withIndex_outputs.pkl")

## #Rimuovi indici
## drop_indexes_sql = [
##     "DROP INDEX idx_genres_artist_id_genre ON genres_artist;",
##     "DROP INDEX idx_tracks_artists_artist_id ON tracks_artists;",
##     "DROP INDEX idx_tracks_artists_track_artist ON tracks_artists;",
##     "DROP INDEX idx_tracks_info_id ON tracks_info;",
##     "DROP INDEX idx_tracks_info_release_date ON tracks_info;"
## ]
## 
## for index in drop_indexes_sql:
##     try:
##         mysql_cursor.execute(index)
##         print(f"Rimosso indice: {index}")
##     except mysql.connector.Error as err:
##         print(f"Errore su {index}: {err}")


# Chiudi connessione
mysql_cursor.close()
mysql_conn.close()
