import json
import logging
from pymongo import MongoClient
import pandas as pd
import ast
from pymongo.errors import BulkWriteError


def load_mongodb():
    client = MongoClient("mongodb://root:pass@localhost:27017/spotify?authSource=admin")
    db = client.spotify
    artist_collection = db["artists"]
    tracks_collection = db["tracks"]

    
    df2 = pd.read_csv('/home/dans/Documents/Uni/DM_project/files/modified/tracks.csv', encoding='utf-8', encoding_errors='replace')
    
    # 2) Funzione di parsing JSON per trasformare ["a","b"] in lista Python
    def parse_list(cell):
        return json.loads(cell) if pd.notna(cell) else []

    # 3) Applico il parsing alle colonne
    df2['artists']    = df2['artists'].apply(parse_list)
    df2['id_artists'] = df2['id_artists'].apply(parse_list)
    successi = 0
    fallimenti = 0
    for idx, row in df2.iterrows():
        doc = row.to_dict()
        try:
            tracks_collection.insert_one(doc)
            successi += 1
        except Exception as e:
            # logga timestamp, indice, errore e documento
            logging.error(f"Riga {idx} non inserita: {e}\n{doc}")
            fallimenti += 1

    # 6) Report a video
    print(f"Inserimenti riusciti: {successi}")
    print(f"Inserimenti falliti:  {fallimenti} (vedi inserimento_mongodb_errori.log)")
    
    print(f"{tracks_collection.count_documents({})} tracce caricate.")  
    
    df1 = pd.read_csv('/home/dans/Documents/Uni/DM_project/files/modified/artists.csv')

    # Converte la colonna 'genres' da stringa a lista
    df1['genres'] = df1['genres'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

    try:
        artist_collection.insert_many(df1.to_dict(orient='records'), ordered=False)
    except BulkWriteError as e:
        print("Errore inserimento artisti:", e.details)

    print(f"{artist_collection.count_documents({})} artisti caricati.")
    

load_mongodb()