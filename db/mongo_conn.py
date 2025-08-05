from pymongo import MongoClient

def get_mongo_collection():
    client = MongoClient("mongodb://root:pass@localhost:27017/spotify?authSource=admin")
    db = client.spotify
    return db