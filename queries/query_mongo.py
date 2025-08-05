import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mongo_conn import get_mongo_collection

collection = get_mongo_collection()
results = collection.tracks.find({"artists": "['The Beatles']"})
for r in results:
    print(r["name"])