import os
from pymongo import MongoClient

def get_connection():

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is missing")

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000
    )

    db = client["school"]

    return db
