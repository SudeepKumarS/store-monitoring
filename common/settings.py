import os

from dotenv import load_dotenv

# Loading the environment variables from .env file
load_dotenv(override=True)


# Getting the data from the env file and assigning them into variables
MONGO_CONNECTION = os.getenv("MONGO_CONNECTION")
DB_NAME = os.getenv("DB_NAME")
STORE_ACTIVITY_COLLECTION = os.getenv("STORE_ACTIVITY_COLLECTION")
BUSINEES_HOURS_COLLECTION = os.getenv("BUSINEES_HOURS_COLLECTION")
STORE_TIMEZONE_COLLECTION = os.getenv("STORE_TIMEZONE_COLLECTION")
REPORT_STATUS_COLLECTION = os.getenv("REPORT_STATUS_COLLECTION")


if not all(
    [MONGO_CONNECTION, DB_NAME, STORE_ACTIVITY_COLLECTION, BUSINEES_HOURS_COLLECTION, STORE_TIMEZONE_COLLECTION]
):
    raise ValueError("One or more required environment variables are not set.")
