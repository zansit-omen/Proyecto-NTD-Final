from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

cliente = MongoClient(MONGO_URI)
DbNoSQL = cliente["chats_db"]
chats = DbNoSQL["chats"]