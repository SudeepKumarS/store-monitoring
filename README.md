# Store/Restaurant Monitoring System

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Interpolation Logic](#interpolation-logic)
- [Output schema](#output-data)


## Overview

Loop Restaurant Monitoring System is a backend application that helps restaurant owners monitor the online/offline status of their stores during business hours. It provides two main APIs: `/trigger_report` for generating reports and `/get_report` for checking report status and retrieving CSV reports.

The system ingests data from three sources:
1. Store Activity Data (CSV): Contains store activity status (active or inactive) and timestamps (in UTC).
2. Business Hours Data (CSV): Specifies the business hours for each store in local time.
3. Timezone Data (CSV): Contains the timezone for each store.

The application loads this data into a MongoDB collections and performs interpolation to calculate uptime and downtime within business hours for different time intervals (last hour, last day, and last week).


## Project Structure

The project is structured as follows:
- `app.py`: Main FastAPI application containing API endpoints.
- `common/connections.py`: Database connection to MongoDB.
- `common/helper.py`: Interpolation logic for calculating uptime and downtime and other helper functions.
- `common/settings.py`: Loading the required environment variables.
- `data/`: Folder containing sample CSV data files.
- `requirements.txt`: List of project dependencies.
- `README.md`: Project documentation.

## Requirements

To run this project, you need the following dependencies installed:
- Python 3.9+
- FastAPI
- MongoDB - Install a local mongo server/run a mongo docker image
- Required Python packages (see `requirements.txt`)

## Setup

1. Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/loop-restaurant-monitoring.git
cd loop-restaurant-monitoring
```

2. Create a virtual environment and then install project dependencies using pip:

```bash
python3 -m venv <env-name>
pip install -r requirements.txt
```

3. Configure the database connection by editing `settings.py` and specifying your database details (e.g., MongoDB URL). Also, the sample datasets in the CSV file should be processed and loaded into the MongoDB collections.

4. Load sample data into the database using the provided CSV files:
   - Store Activity Data (`data/store_activity.csv`)
   - Business Hours Data (`data/business_hours.csv`)
   - Timezone Data (`data/timezones.csv`)
You can load the data by running the data_loader.py file in the root directory of the project. You can run it using the following command.
```bash
python data_loader.py
```

## Usage

To run the FastAPI application, execute the following command in the root directory of the project:

```bash
python app.py
```

The application will start on `http://localhost:8000`.

## API Endpoints

- `/trigger_report` (POST): Trigger report generation and receive a unique `report_id` in response.
- `/get_report` (GET): Check the status of a report or retrieve the CSV report using a `report_id`.

## Database

The application uses MongoDB to store and manage data efficiently. To make this project work, we need to load the CSV files data into database.

## Output data

Reports are generated based on the data and interpolation logic. They include the following information for each store:
- Store ID
- Uptime and downtime for the last hour (in minutes)
- Uptime and downtime for the last day (in hours)
- Uptime and downtime for the last week (in hours)