import mysql.connector
import time
import pandas as pd
import psutil

# === Percorso risultati ===
dst_for_results = "/home/dans/Documents/Uni/DM_project/outputs/mySQL/"
run_num = 6  # numero di volte che ogni query viene eseguita

# === Funzione per trovare il processo mysqld ===
def get_mysql_process():
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'] and 'mysqld' in p.info['name']:
                print(f"Trovato processo MySQL: PID {p.pid}")
                return p
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    raise RuntimeError("Processo mysqld non trovato! Assicurati che MySQL sia in esecuzione.")

# === Funzione per misurare tempo e memoria ===
def measure_query_performance(cursor, query, mysql_proc):
    start_time = time.perf_counter()

    cursor.execute(query)
    result = cursor.fetchall()

    end_time = time.perf_counter()
    exec_time_ms = (end_time - start_time) * 1000

    # memoria totale del processo mysqld (in KB)
    mem_used_kb = mysql_proc.memory_info().rss / 1024  

    return exec_time_ms, mem_used_kb, result

# === Connessione a MySQL ===
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="user",
    password="pass",
    database="spotify"
)
mysql_cursor = mysql_conn.cursor(dictionary=True)

# Ottieni il processo mysqld
mysql_proc = get_mysql_process()

# === Query SQL ===
queries = {
    "Q1": """
SELECT 
    ta.artist_name,
    ROUND(AVG(CAST(t.popularity AS DECIMAL(10,2))), 2) AS avg_popularity,
    COUNT(*) AS n_tracks
FROM spotify.tracks_artists ta
JOIN tracks_info t ON t.id = ta.track_id AND t.popularity IS NOT NULL
GROUP BY ta.artist_id, ta.artist_name
HAVING COUNT(*) >= 60
ORDER BY avg_popularity DESC
LIMIT 20;
    """,
    "Q2": """
        SELECT tracks.name
        FROM tracks
        WHERE JSON_CONTAINS(tracks.artists, '"Eminem"') and JSON_LENGTH(tracks.artists) = 1
        ORDER BY tracks.popularity DESC LIMIT 50;
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

# === Esecuzione SENZA indici ===
execution_data = []

print("\n--- Esecuzione senza indici ---")
for qname, query in queries.items():
    for i in range(run_num):
        exec_time, mem_used, result = measure_query_performance(mysql_cursor, query, mysql_proc)
        print(f"{qname} - Run #{i+1}: Time = {exec_time:.2f} ms | MySQL Mem = {mem_used/1024:.2f} MB")
        execution_data.append([qname, i+1, exec_time, mem_used])

# Salva risultati
df_noindex = pd.DataFrame(execution_data, columns=["Query", "Run", "ExecutionTime_ms", "MySQLMemoryUsed_KB"])
df_noindex.to_csv(dst_for_results + "Mysql_noIndex_perf.csv", index=False)

# === Creazione Indici ===
indexes_sql = [
    "CREATE INDEX idx_genres_artist_id_genre ON genres_artist (id, genre);",
    "CREATE INDEX idx_tracks_artists_artist_id ON tracks_artists (artist_id);",
    "CREATE INDEX idx_tracks_artists_track_artist ON tracks_artists (track_id, artist_id);",
    "CREATE INDEX idx_tracks_info_id ON tracks_info (id);",
    "CREATE INDEX idx_tracks_info_release_date ON tracks_info (release_date);"
]

print("\n--- Creazione indici ---")
for index in indexes_sql:
    try:
        mysql_cursor.execute(index)
        print(f"Creato indice: {index}")
    except mysql.connector.Error as err:
        print(f"Errore su {index}: {err}")

# === Esecuzione CON indici ===
execution_data = []

print("\n--- Esecuzione con indici ---")
for qname, query in queries.items():
    for i in range(run_num):
        exec_time, mem_used, result = measure_query_performance(mysql_cursor, query, mysql_proc)
        print(f"{qname} - Run #{i+1}: Time = {exec_time:.2f} ms | MySQL Mem = {mem_used/1024:.2f} MB")
        execution_data.append([qname, i+1, exec_time, mem_used])

# Salva risultati
df_index = pd.DataFrame(execution_data, columns=["Query", "Run", "ExecutionTime_ms", "MySQLMemoryUsed_KB"])
df_index.to_csv(dst_for_results + "Mysql_withIndex_perf.csv", index=False)

# === Rimozione Indici (opzionale) ===
# drop_indexes_sql = [
#     "DROP INDEX idx_genres_artist_id_genre ON genres_artist;",
#     "DROP INDEX idx_tracks_artists_artist_id ON tracks_artists;",
#     "DROP INDEX idx_tracks_artists_track_artist ON tracks_artists;",
#     "DROP INDEX idx_tracks_info_id ON tracks_info;",
#     "DROP INDEX idx_tracks_info_release_date ON tracks_info;"
# ]
#
# print("\n--- Rimozione indici ---")
# for index in drop_indexes_sql:
#     try:
#         mysql_cursor.execute(index)
#         print(f"Rimosso indice: {index}")
#     except mysql.connector.Error as err:
#         print(f"Errore su {index}: {err}")

# === Chiusura connessione ===
mysql_cursor.close()
mysql_conn.close()

print("\n✅ Test completato. Risultati salvati in:")
print(" - Mysql_noIndex_perf.csv")
print(" - Mysql_withIndex_perf.csv")
