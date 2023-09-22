from bson import ObjectId
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from common.helpers import start_report_generation

from common.connections import report_status_collection

from fastapi import FastAPI, BackgroundTasks, HTTPException

from common.models import ReportStatus, ReportStatusModel


app = FastAPI()

# Endpoint for the root page
@app.get("/")
def home_page():
    return {"Hi!": "This is a development server"}


# Endpoint to trigger report generation
@app.post("/trigger_report/")
async def trigger_report(background_tasks: BackgroundTasks):
    try:
        # Generating the report model
        report_model = ReportStatusModel()

        # Calling the function to generate the report in the background
        background_tasks.add_task(start_report_generation, report_model.id)

        # Updating the report model in the Database
        report_status_collection.insert_one(report_model.to_database())

        return report_model.model_dump()
    except Exception as err:
        return HTTPException(status_code=500, detail=f"Internal Server Error: {err}")


# Endpoint to get report status and retrieve the report if completed
@app.get("/get_report/")
async def get_report(report_id: str):
    try:
        report_bson = report_status_collection.find_one({"_id": ObjectId(report_id)})

        if report_bson is None:
            return HTTPException(status_code=404, detail="Report with this ID is not found")
        
        report_model = ReportStatusModel.from_database(report_bson)

        if report_model.status == ReportStatus.completed.value:
            # The csv file is stored in the current directory
            filename = f"report_{report_id}.csv"

            return FileResponse(filename, media_type="text/csv")
        
        return report_model.model_dump()
    except Exception as err:
        return HTTPException(status_code=500, detail=f"Internal Server Error: {err}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, workers=6)
