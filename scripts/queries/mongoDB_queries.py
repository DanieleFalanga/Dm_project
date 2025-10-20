from pymongo import MongoClient
from pymongo.errors import ExecutionTimeout
import time
import pandas as pd
import psutil

# === Config ===
uri = "mongodb://root:pass@localhost:27017/"
db_name = "spotify"
runs_per_pipeline = 6
dst_for_results = "/home/dans/Documents/Uni/DM_project/outputs/MongoDB/"
TIMEOUT_MS = 120_000  # 2 minuti

# === Connessione ===
client = MongoClient(uri)
db = client[db_name]
artists = db["artists"]
tracks = db["tracks_info"]
genres_artist = db["genres_artist"]

# === Funzione per ottenere il processo mongod ===
def get_mongo_process():
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'] and 'mongod' in p.info['name']:
                print(f"Trovato processo MongoDB: PID {p.pid}")
                return p
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    raise RuntimeError("Processo mongod non trovato! Assicurati che MongoDB sia in esecuzione.")

# === Ottieni il processo MongoDB ===
mongo_proc = get_mongo_process()

# === Pipelines ===
pipeline_Q1 = [
    {"$match": {"popularity": {"$ne": None}}},
    {"$unwind": "$id_artists"},
    {"$set": {"popularity": {"$toDouble": "$popularity"}}},
    {"$group": {"_id": "$id_artists", "avg_popularity": {"$avg": "$popularity"}, "n_tracks": {"$sum": 1}}},
    {"$match": {"n_tracks": {"$gte": 60}}},
    {"$sort": {"avg_popularity": -1}},
    {"$limit": 20},
    {"$lookup": {"from": "artists", "localField": "_id", "foreignField": "id", "as": "artist_info"}},
    {"$unwind": "$artist_info"},
    {"$project": {"_id": 0, "artist_id": "$_id", "name": "$artist_info.name",
                  "avg_popularity": {"$round": ["$avg_popularity", 2]}, "n_tracks": 1}}
]

pipeline_Q2 = [
    {"$match": {"artists": "Eminem"}},
    {"$match": {"$expr": {"$eq": [{"$size": "$artists"}, 1]}}},
    {"$sort": {"popularity": -1}},
    {"$limit": 50},
    {"$project": {"_id": 0, "name": 1}}
]

pipeline_Q3 = [
    {"$project": {"id": 1, "name": 1, "id_artists": 1, "popularity": 1, "release_date": 1}},
    {"$unwind": "$id_artists"},
    {"$lookup": {"from": "genres_artist", "localField": "id_artists", "foreignField": "id", "as": "genre_artist"}},
    {"$unwind": "$genre_artist"},
    {"$group": {"_id": {"year": "$release_date", "genre": "$genre_artist.genre"},
                "track_count": {"$sum": 1}, "avg_popularity": {"$avg": "$popularity"}}},
    {"$match": {"track_count": {"$gte": 200}}},
    {"$sort": {"_id.year": 1, "avg_popularity": -1}},
    {"$group": {"_id": "$_id.year", "genre": {"$first": "$_id.genre"},
                "avg_popularity": {"$first": "$avg_popularity"}, "track_count": {"$first": "$track_count"}}},
    {"$sort": {"_id": 1}},
    {"$project": {"_id": 0, "release_year": "$_id", "genre": 1, "avg_popularity": 1, "track_count": 1}}
]

pipelines = {
    "Q1_top_artists_by_avg_pop": pipeline_Q1,
    "Q2_eminem_solo_tracks": pipeline_Q2,
    "Q3_top_genre_per_year": pipeline_Q3,
}

# === Funzione di esecuzione fase (senza/con indici) ===
def run_phase(label: str, create_indexes: bool = False):
    created = []
    if create_indexes:
        created = [
            tracks.create_index([("id", 1)]),
            tracks.create_index([("release_date", 1)]),
            tracks.create_index([("popularity", 1)]),
            genres_artist.create_index([("id", 1)]),
        ]

    execution_data = []

    for name, pipe in pipelines.items():
        for run_idx in range(runs_per_pipeline):
            try:
                t0 = time.perf_counter()
                cursor = tracks.aggregate(pipe, allowDiskUse=True, maxTimeMS=TIMEOUT_MS)
                docs = list(cursor)
                t1 = time.perf_counter()
                exec_ms = (t1 - t0) * 1000.0

                # Misura memoria totale del processo mongod in KB
                mem_used_kb = mongo_proc.memory_info().rss / 1024

                print(f"{label} | {name} - run {run_idx+1}/{runs_per_pipeline}: "
                      f"{exec_ms:.2f} ms | Mem: {mem_used_kb/1024:.2f} MB | rows={len(docs)}")

            except ExecutionTimeout:
                exec_ms = float(TIMEOUT_MS)
                mem_used_kb = mongo_proc.memory_info().rss / 1024
                docs = []
                print(f"{label} | {name} - run {run_idx+1}/{runs_per_pipeline}: TIMEOUT (>= {TIMEOUT_MS} ms)")

            except Exception as e:
                exec_ms = float('nan')
                mem_used_kb = mongo_proc.memory_info().rss / 1024
                docs = []
                print(f"{label} | {name} - run {run_idx+1}: ERROR -> {e}")

            execution_data.append([name, run_idx+1, exec_ms, mem_used_kb, len(docs)])

    # === Salvataggio risultati ===
    df_perf = pd.DataFrame(execution_data,
                           columns=["Query", "Run", "ExecutionTime_ms", "MongoMemoryUsed_KB", "NumDocs"])
    df_perf.to_csv(f"{dst_for_results}Mongo_{label}_perf.csv", index=False)
    print(df_perf)

    # cleanup indici se creati
    if create_indexes and created:
        try:
            tracks.drop_index([("id", 1)])
        except Exception:
            pass
        try:
            tracks.drop_index([("release_date", 1)])
        except Exception:
            pass
        try:
            genres_artist.drop_index([("id", 1)])
        except Exception:
            pass

# === Fasi ===
print("\n--- Esecuzione senza indici ---")
run_phase(label="noIndex", create_indexes=False)

print("\n--- Esecuzione con indici ---")
run_phase(label="withIndex", create_indexes=True)

# === Chiusura ===
client.close()
print("\n✅ Test completato. Risultati salvati in:")
print(" - Mongo_noIndex_perf.csv")
print(" - Mongo_withIndex_perf.csv")
