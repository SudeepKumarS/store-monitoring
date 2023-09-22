from pymongo import MongoClient

from common.settings import (
    BUSINEES_HOURS_COLLECTION,
    DB_NAME,
    MONGO_CONNECTION,
    REPORT_STATUS_COLLECTION,
    STORE_ACTIVITY_COLLECTION,
    STORE_TIMEZONE_COLLECTION,
)

# Initiating Mongo Client and Connections
monog_client = MongoClient(MONGO_CONNECTION)
db = monog_client.get_database(DB_NAME)
store_activity_collection = db.get_collection(STORE_ACTIVITY_COLLECTION)
business_hours_collection = db.get_collection(BUSINEES_HOURS_COLLECTION)
store_timezone_collection = db.get_collection(STORE_TIMEZONE_COLLECTION)
report_status_collection = db.get_collection(REPORT_STATUS_COLLECTION)
