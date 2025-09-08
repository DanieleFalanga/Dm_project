Analisi da svolgere:
- [ ] Query senza indici sia per SQL che per Mongo
        - Manca da implementare la query 3 in MongoDB
- [ ] Query con indici

-[X] **Q1. Top artisti per popolarità media (solo artisti con ≥3 tracce)** 
Obiettivo: aggregazioni + join/lookup.
Indici fase B: `tracks(artist_id, popularity)` / `artists(artist_id)` • Mongo: `tracks{artist_id:1,popularity:-1}`, `artists{artist_id:1}`.
Nota MySQL: se `tracks.artist_id` è JSON array, usa `JSON_TABLE` o tabella ponte.

- [X] **Q2. Tracce di un artista ordinate per popolarità (top 50)**  
Obiettivo: filtro + sort + limit.
Indici: `tracks(artist_id, popularity DESC)` • Mongo: `{artist_id:1, popularity:-1}`.

- [X] **Q3. MIglior Genere per ogni anno con un numero minimo di canzoni di 200**  

Per ogni query, fare almeno 6/7 run in modo da riempire la cache e far si che gli output siano piu affidabili. ù



