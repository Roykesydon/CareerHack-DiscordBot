from core.config import CONFIG
from pymongo import MongoClient

mongo_db_url = (
    f"mongodb://{CONFIG['mongo']['user']}:{CONFIG['mongo']['password']}@"
    + f"{CONFIG['mongo']['host']}:{CONFIG['mongo']['port']}"
)
mongo_client = MongoClient(mongo_db_url)
mongo_database = mongo_client[CONFIG["mongo"]["db"]]
