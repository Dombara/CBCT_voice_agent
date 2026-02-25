import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    os.getenv("MONGO_URI"),
    serverSelectionTimeoutMS=3000  # fail fast
)

db = client["fyp_db"]

doctor_collection = db["doctor_collection"]
appointment_collection = db["appointment_collection"]
# slot_collection = db["slot_collection"]