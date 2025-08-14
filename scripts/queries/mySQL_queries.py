import mysql.connector
import time

# Connessione a MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="user",
    password="pass",
    database="spotify"
)

mysql_cursor = mysql_conn.cursor(dictionary=True)

Q1 = """
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
    """

Q2 = """
    SELECT tracks.name
    FROM tracks
    WHERE JSON_CONTAINS(tracks.artists, '"Eminem"') and JSON_LENGTH(tracks.artists) = 1
    ORDER BY tracks.popularity DESC LIMIT 50 
    """

Q3 = """
WITH exploded AS (
  SELECT
    t.release_date AS year,
    t.popularity,
    g.genre
  FROM tracks t
  JOIN JSON_TABLE(t.id_artists, '$[*]'
       COLUMNS (artist_id VARCHAR(25) PATH '$')) jt
  JOIN artists a ON a.id = jt.artist_id
  JOIN JSON_TABLE(a.genres, '$[*]'
       COLUMNS (genre VARCHAR(255) PATH '$')) AS g
),
genre_year AS (
  SELECT
      year,
      genre,
      AVG(popularity) AS avg_popularity,
      SUM(popularity) AS sum_popularity,
      COUNT(*)        AS n_tracks
  FROM exploded
  GROUP BY year, genre
  HAVING COUNT(*) > 200  -- filtro minimo 200 canzoni per anno/genere
)
SELECT year, genre, avg_popularity, sum_popularity, n_tracks
FROM (
  SELECT gy.*,
         ROW_NUMBER() OVER (PARTITION BY year ORDER BY avg_popularity DESC) AS rn
  FROM genre_year gy
) x
WHERE rn <= 3
ORDER BY year, rn;
"""

## Scrivi le query nel formato soprastante e nominarle nel set sottostante 

queries = [Q1,Q2, Q3]

for query_num, query in enumerate(queries, start=1):
    for run_num in range(6):
        # Inizio misurazione
        start_time = time.perf_counter()

        mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()

        # Fine misurazione
        end_time = time.perf_counter()

        # Calcolo tempo
        execution_time = (end_time - start_time) * 1000  # in millisecondi
        print(f"Query #{query_num} - Run #{run_num + 1} - Execution Time: {execution_time:.2f} ms")

        #TODO
        # Inserire i tempi in pandas

# Chiudi connessione
mysql_cursor.close()
mysql_conn.close()
