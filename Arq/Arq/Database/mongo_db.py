from pymongo import MongoClient

MONGO_URI = "mongodb+srv://Admin:ProLink123@prolink.bcknvo4.mongodb.net/chats_db?appName=ProLink"

client = MongoClient(MONGO_URI)
DbNoSQL = client["chats_db"]
chats = DbNoSQL["chats"]