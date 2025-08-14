from pymongo import MongoClient
import time
import pprint

# se lo script gira sull'host:
uri = "mongodb://root:pass@localhost:27017/"

client = MongoClient(uri)
db = client["spotify"]
artists =db["artists"] 
tracks = db["tracks"]

pipeline_Q1 = [
    {"$match": {"popularity": {"$ne": None}}},            # filtro base
    {"$unwind": "$id_artists"},                           # esplodi l'array di artisti
    {"$set": {"popularity": {"$toDouble": "$popularity"}}},  # <- rimuovi se è già numerica
    {"$group": {                                          # media e conteggio per artista
        "_id": "$id_artists",
        "avg_popularity": {"$avg": "$popularity"},
        "n_tracks": {"$sum": 1}
    }},
    {"$match": {"n_tracks": {"$gte": 60}}},               # HAVING
    {"$sort": {"avg_popularity": -1}},
    {"$limit": 20},
    {"$lookup": {                                         # arricchisci con info artista
        "from": "artists",
        "localField": "_id",
        "foreignField": "id",    # <-- se la chiave in artists è "artist_id", metti "artist_id"
        "as": "artist_info"
    }},
    {"$unwind": "$artist_info"},
    {"$project": {
        "_id": 0,
        "artist_id": "$_id",
        "name": "$artist_info.name",
        "avg_popularity": {"$round": ["$avg_popularity", 2]},
        "n_tracks": 1
    }}
]

pipeline_Q2 = [
    {"$match": {"artists": "Eminem"}},
    {"$match": {"$expr": {"$eq": [{"$size": "$artists"}, 1]}}},  # solo tracce con 1 solo artista
    {"$sort": {"popularity": -1}},
    {"$limit": 50},
    {"$project": {"_id": 0, "name": 1}}
]

pipeline_Q3 = [
   # 1) Seleziona i campi utili e normalizza release_date -> year (intero)
    {
        "$project": {
            "track_id": "$id",
            "popularity": "$popularity",
            "year": {"$toInt": "$release_date"},
            "artist_ids": {"$ifNull": ["$id_artists", "$artists"]}  # usa quello che hai
        }
    },
    {"$match": {"year": {"$ne": None}}},

    # 2) Lookup agli artisti e dedup dei generi a livello di TRACCIA
    {
        "$lookup": {
            "from": "artists",
            "let": {"artist_ids": "$artist_ids"},
            "pipeline": [
                {"$match": {"$expr": {"$in": ["$id", "$$artist_ids"]}}},
                {"$project": {"_id": 0, "genres": {"$ifNull": ["$genres", []]}}}
            ],
            "as": "artists_docs"
        }
    },
    # track_genres = unione (dedup) di tutti i generi degli artisti della traccia
    {
        "$project": {
            "year": 1,
            "popularity": 1,
            "track_genres": {
                "$reduce": {
                    "input": "$artists_docs.genres",
                    "initialValue": [],
                    "in": {"$setUnion": ["$$value", "$$this"]}
                }
            }
        }
    },
    {"$unwind": "$track_genres"},

    # 3) Aggrega per (anno, genere)
    {
        "$group": {
            "_id": {"year": "$year", "genre": "$track_genres"},
            "tracks_count": {"$sum": 1},
            "avg_popularity": {"$avg": "$popularity"}
        }
    },

    # 4) Ordina per anno e poi per metriche per estrarre il top
    {"$sort": {"_id.year": 1, "tracks_count": -1, "avg_popularity": -1, "_id.genre": 1}},

    # 5) Prendi il primo per ogni anno
    {
        "$group": {
            "_id": "$_id.year",
            "genre": {"$first": "$_id.genre"},
            "tracks_count": {"$first": "$tracks_count"},
            "avg_popularity": {"$first": "$avg_popularity"}
        }
    },

    # 6) Output finale
    {
        "$project": {
            "_id": 0,
            "year": "$_id",
            "genre": 1,
            "tracks_count": 1,
            "avg_popularity": {"$round": ["$avg_popularity", 2]}
        }
    },
    {"$sort": {"year": 1}}
]

# Scrivere le query nel formato pipelines_Qn = [] e inserire il nome nel set sottostante 

pipelines = [pipeline_Q1, 
             pipeline_Q2,
             pipeline_Q3]

for pipeline_num,pipeline in enumerate(pipelines, start = 1):
    for run_num in range(6):

        start_time = time.perf_counter()

        result = tracks.aggregate(pipeline, allowDiskUse =True)

        end_time = time.perf_counter()

        execution_time = (end_time - start_time) * 1000  # in millisecondi
        print(f"Query #{pipeline_num} - Run #{run_num + 1} - Execution Time: {execution_time:.2f} ms")


client.close()