from pymongo import MongoClient
from pymongo.errors import ExecutionTimeout
import time
import pandas as pd

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

# === Pipelines (le tue) ===
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
    "Q3_top_genre_per_year": pipeline_Q3,  # questa è quella lenta
}

def run_phase(label: str, create_indexes: bool = False):
    # opzionale: crea indici per la fase "withIndex"
    created = []
    if create_indexes:
        created = [
            tracks.create_index([("id", 1)]),
            tracks.create_index([("release_date", 1)]),
            tracks.create_index([("popularity", 1)]),
            genres_artist.create_index([("id", 1)]),
        ]

    # matrici
    execution_times = {name: [] for name in pipelines.keys()}
    outputs = {name: [] for name in pipelines.keys()}

    # esecuzione con timeout
    for name, pipe in pipelines.items():
        for run_idx in range(runs_per_pipeline):
            try:
                t0 = time.perf_counter()
                cursor = tracks.aggregate(pipe, allowDiskUse=True, maxTimeMS=TIMEOUT_MS)
                docs = list(cursor)  # se supera TIMEOUT_MS solleva ExecutionTimeout
                t1 = time.perf_counter()
                exec_ms = (t1 - t0) * 1000.0
                print(f"{label} | {name} - run {run_idx+1}/{runs_per_pipeline}: {exec_ms:.2f} ms | rows={len(docs)}")
            except ExecutionTimeout:
                # timeout: assegna 10 minuti esatti e risultato vuoto (o un sentinel)
                exec_ms = float(TIMEOUT_MS)
                docs = []
                print(f"{label} | {name} - run {run_idx+1}/{runs_per_pipeline}: TIMEOUT (>= {TIMEOUT_MS} ms)")
            except Exception as e:
                # opzionale: in caso di errore non previsto, marca come NaN
                exec_ms = float('nan')
                docs = []
                print(f"{label} | {name} - run {run_idx+1}: ERROR -> {e}")

            execution_times[name].append(exec_ms)
            outputs[name].append(docs)

    # dataframe matrice
    df_times = pd.DataFrame.from_dict(
        execution_times, orient="index",
        columns=[f"run_{i+1}" for i in range(runs_per_pipeline)]
    )
    print(df_times)

    # salvataggi
    df_times.to_csv(f"{dst_for_results}Mongo_{label}_times.csv", index=True)
    pd.to_pickle(outputs, f"{dst_for_results}Mongo_{label}_outputs.pkl")

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

# === Fasi: senza indici e con indici ===
run_phase(label="noIndex", create_indexes=False)
run_phase(label="withIndex", create_indexes=True)

# === Chiusura ===
client.close()
