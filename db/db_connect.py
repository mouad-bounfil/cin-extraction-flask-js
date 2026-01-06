from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()


# i want to connect to the database
def get_db():
    try:
        client = MongoClient(getenv("MONGO_URI"))
        print("Connected to the database ✅")
        return client["mydatabase"]
    except Exception as e:
        print(e)
        return None
