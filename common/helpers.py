import csv
from datetime import datetime, timedelta
import traceback
from bson import ObjectId
import pytz

from common.connections import store_activity_collection, business_hours_collection, store_timezone_collection, report_status_collection
from common.models import ReportStatus


def get_data_and_process(store_id: str) -> dict:
    """
    Method to get the data from the database, process, and validate it.
    """
    try:
        store_log_data = {}
        store_status_data_bson = store_activity_collection.find({"store_id": store_id})

        for data_log in store_status_data_bson:
            if store_id not in store_log_data:
                store_log_data[store_id] = []
            datetime_obj = data_log["timestamp_utc"]
            store_log_data[store_id].append((datetime_obj, data_log["status"]))

        return store_log_data

    except Exception as e:
        print(f"Error in get_data_and_process for store {store_id}: {e}")
        return {}


def get_active_business_hours(store_id: str) -> dict:
    """
    Get the active business hours of a store.
    """
    try:
        business_hours = {}
        weekdays_set = [_ for _ in range(7)]

        for week_day in weekdays_set:
            business_hrs_obj = business_hours_collection.find_one({"store_id": store_id, "day": week_day})
            if business_hrs_obj is None:
                start_time_local_str, end_time_local_str = "00:00:00", "23:59:59"
            else:
                start_time_local_str, end_time_local_str = business_hrs_obj["start_time_local"], business_hrs_obj["end_time_local"]
            start_time_local = datetime.strptime(start_time_local_str, "%H:%M:%S").time()
            end_time_local = datetime.strptime(end_time_local_str, "%H:%M:%S").time()
            business_hours[(store_id, week_day)] = (start_time_local, end_time_local)

        return business_hours

    except Exception as e:
        print(f"Error in get_active_business_hours for store {store_id}: {e}")
        return {}


def get_timezone_of_store(store_id: str) -> str:
    """
    Get the timezone of a store. Default to 'America/Chicago' if not found.
    """
    try:
        timezone_obj = store_timezone_collection.find_one({"store_id": store_id}, {"timezone": 1})
        return timezone_obj["timezone"] if timezone_obj else "America/Chicago"

    except Exception as e:
        print(f"Error in get_timezone_of_store for store {store_id}: {e}")
        return "America/Chicago"


def filtered_business_observations(store_id: str) -> list:
    """
    Retrieve filtered active observations within the business hours of a store.
    """
    try:
        filtered_observations = []
        stores_observations = get_data_and_process(store_id)

        if not stores_observations:
            return []

        business_hours_data = get_active_business_hours(store_id)
        store_timezone = get_timezone_of_store(store_id)

        for obs in stores_observations[store_id]:
            timestamp_utc, obs_status = obs
            local_timestamp = timestamp_utc.astimezone(pytz.timezone(store_timezone))
            local_day = local_timestamp.weekday()
            local_time = local_timestamp.time()
            start_time, end_time = business_hours_data[(store_id, local_day)]

            if start_time <= local_time <= end_time:
                filtered_observations.append(obs)

        return filtered_observations

    except Exception as e:
        print(f"Error in filtered_business_observations for store {store_id}: {e}")
        return []


def calculate_uptime_and_downtime(store_id):
    """
    Calculate the total uptime and downtime of a store based on the data provided.
    """
    try:
        uptime_last_hour = 0
        uptime_last_day = 0
        uptime_last_week = 0
        downtime_last_hour = 0
        downtime_last_day = 0
        downtime_last_week = 0

        now = datetime.strptime("2023-01-21 08:04:26.177456", "%Y-%m-%d %H:%M:%S.%f")
        last_hour_start = now - timedelta(hours=1)
        last_day_start = now - timedelta(days=1)
        last_week_start = now - timedelta(weeks=1)

        observations = get_active_business_hours(store_id)
        timestamps_within_business_hours = filtered_business_observations(store_id)
        timestamps_within_business_hours.sort(key=lambda x: x[0])

        for i in range(len(timestamps_within_business_hours) - 1):
            current_time = timestamps_within_business_hours[i][0]
            next_time = timestamps_within_business_hours[i + 1][0]
            # Calculatinng based on any match of the timstamp window and active status
            status = "active" if any(current_time <= obs["timestamp_utc"] <= next_time for obs in observations if obs[1] == "active") else "inactive"

            if status == "active":
                uptime_last_hour += (next_time - current_time).total_seconds() / 60
                uptime_last_day += (next_time - current_time).total_seconds() / 3600
                uptime_last_week += (next_time - current_time).total_seconds() / 3600
            else:
                downtime_last_hour += (next_time - current_time).total_seconds() / 60
                downtime_last_day += (next_time - current_time).total_seconds() / 3600
                downtime_last_week += (next_time - current_time).total_seconds() / 3600

        if timestamps_within_business_hours:
            last_timestamp = timestamps_within_business_hours[-1][0]
            if last_timestamp > last_hour_start:
                uptime_last_hour += (last_timestamp - last_hour_start).total_seconds() / 60
            if last_timestamp > last_day_start:
                uptime_last_day += (last_timestamp - last_day_start).total_seconds() / 3600
            if last_timestamp > last_week_start:
                uptime_last_week += (last_timestamp - last_week_start).total_seconds() / 3600

        return {
            "store_id": store_id,
            "uptime_last_hour": uptime_last_hour,
            "uptime_last_day": uptime_last_day,
            "uptime_last_week": uptime_last_week,
            "downtime_last_hour": downtime_last_hour,
            "downtime_last_day": downtime_last_day,
            "downtime_last_week": downtime_last_week,
        }

    except Exception as e:
        print(f"Error in calculate_uptime_and_downtime for store {store_id}: {e}")
        return {}

async def generate_report(report_id: str):
    """
    Method to start the report generation and update the status of the generation
    in the database
    """
    try:
        # Getting the store IDs to start the report generation
        store_ids = store_timezone_collection.distinct("store_id")

        # Generating a CSV file with the report ID
        csv_filename = f"report_{report_id}.csv"


        csv_headers = [
            "store_id",
            "uptime_last_hour",
            "uptime_last_day",
            "uptime_last_week",
            "downtime_last_hour",
            "downtime_last_day",
            "downtime_last_week",
        ]

        # Opening a CSV file to write the data
        with open(csv_filename, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            
            # Inserting the header row
            writer.writeheader()
            
            for s_id in store_ids:
                report_data = calculate_uptime_and_downtime(s_id)
                if report_data:
                    writer.writerow(report_data)
                    
        # Updating the status of the report in the DB
        report_status_collection.update_one({"_id": ObjectId(report_id)}, {"$set": {"status": ReportStatus.completed}})
    except Exception as err:
        print(f"Failed to generate the report for ID {report_id}")
        print(f"Error: {err}")
        print(traceback.format_exc())
        # Updating the status of the report in the DB
        report_status_collection.update_one({"_id": ObjectId(report_id)}, {"$status": ReportStatus.failed})