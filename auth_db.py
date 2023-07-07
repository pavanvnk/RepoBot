import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_db_user = os.getenv("MONGO_DB_USER")
mongo_db_password = os.getenv("MONGO_DB_PASSWORD")

connection = f"mongodb+srv://{mongo_db_user}:{mongo_db_password}@atlascluster.b3klcgw.mongodb.net/"
client = MongoClient(connection)
db = client['discordbot']
collection = db['users']

def set_user_token(user_id, tokens: dict):
    user = {
        'user_id': user_id,
        'tokens': tokens
    }
    collection.replace_one({'user_id': user_id}, user, upsert=True)

def get_user_token(user_id):
    user = collection.find_one({'user_id': user_id})

    if user is None:
        return None

    return user['tokens']