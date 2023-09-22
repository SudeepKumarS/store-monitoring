import csv
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo import collection as pymongo_collection

from common.models import BusinessHoursModel, MongoBaseModel, StoreActivityModel, StoreTimezonesModel

# Loading the environment variables from .env file
load_dotenv("./.env", override=True)

# Getting the data from the env file and assigning them into variables
MONGO_CONNECTION = os.getenv("MONGO_CONNECTION")
DB_NAME = os.getenv("DB_NAME")
STORE_ACTIVITY_COLLECTION = os.getenv("STORE_ACTIVITY_COLLECTION")
BUSINEES_HOURS_COLLECTION = os.getenv("BUSINEES_HOURS_COLLECTION")
STORE_TIMEZONE_COLLECTION = os.getenv("STORE_TIMEZONE_COLLECTION")


# Initiating Mongo Client and Connections
monog_client = MongoClient(MONGO_CONNECTION)
db = monog_client.get_database(DB_NAME)
store_activity_collection = db.get_collection(STORE_ACTIVITY_COLLECTION)
business_hours_collection = db.get_collection(BUSINEES_HOURS_COLLECTION)
store_timezone_collection = db.get_collection(STORE_TIMEZONE_COLLECTION)


def load_csv_data_to_mongodb(collection: pymongo_collection.Collection, csv_path: str, model: MongoBaseModel) -> None:
    """
    Method to load CSV data into the database collections
    """
    try:
        # Opening the CSV file and reading data
        with open(csv_path, "r") as file:
            csv_reader = csv.DictReader(file)
            data = list(csv_reader)

            converted_data = []
            # Converting the timestamp_utc column to datetime
            for entry in data:
                timestamp_str = entry.get("timestamp_utc", None)
                if timestamp_str:
                    # Converting the String UTC timestamp to proper datetime
                    # Only two possibilities in the UTC timestamps -> with and without microseconds
                    try:
                        # Firsting handling the case where the timestamp includes microseconds
                        datetime_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f UTC")
                    except ValueError:
                        # If parsing with microseconds fails, converting without microseconds
                        datetime_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S UTC")
                    entry["timestamp_utc"] = datetime_obj
                model_entry = model(**entry)
                converted_data.append(model_entry.to_database())

            # Inserting data into the database
            collection.insert_many(converted_data)

            # Creating index for store ID - common for all the collections
            collection.create_index("store_id")

            print(f"{len(data)} records inserted into {collection.name} collection.")
    except Exception as err:
        print(f"Failed to upload data for {collection.name}: {err}")


# Mapping the collection, models and the path to the data file
collections_map = {
    store_activity_collection: ("./data/store_activity.csv", StoreActivityModel),
    business_hours_collection: ("./data/business_hours.csv", BusinessHoursModel),
    store_timezone_collection: ("./data/timezones.csv", StoreTimezonesModel),
}


if __name__ == "__main__":
    import time

    start = time.time()
    for col in collections_map:
        load_csv_data_to_mongodb(col, collections_map[col][0], collections_map[col][1])

    print("Finished inserting collections in ", time.time() - start)
