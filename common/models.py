from datetime import datetime
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


# Model for Mongo DB
class MongoBaseModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))

    def to_database(self, *args, **kwargs) -> dict:
        data = self.model_dump(*args, **kwargs)
        data["_id"] = ObjectId(data.pop("id"))
        return data

    @classmethod
    def from_database(cls, data, *args, **kwargs) -> "MongoBaseModel":
        try:
            data["id"] = str(data.pop("_id"))
        except Exception:
            print(data)
        return cls(*args, **data, **kwargs)


# Model for Store activity
class StoreActivityModel(MongoBaseModel):
    store_id: int
    timestamp_utc: datetime
    status: str

    @classmethod
    def from_database(cls, data, *args, **kwargs) -> "StoreActivityModel":
        try:
            data["id"] = str(data.pop("_id"))
        except Exception:
            print(data)
        return cls(*args, **data, **kwargs)


class WeekDaysEnum(str, Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class BusinessHoursModel(MongoBaseModel):
    store_id: int
    day: WeekDaysEnum
    start_time_local: str
    end_time_local: str

    @classmethod
    def from_database(cls, data, *args, **kwargs) -> "BusinessHoursModel":
        try:
            data["id"] = str(data.pop("_id"))
        except Exception:
            print(data)
        return cls(*args, **data, **kwargs)


class StoreTimezonesModel(MongoBaseModel):
    store_id: int
    timezone: Optional[str] = "America/Chicago"

    @classmethod
    def from_database(cls, data, *args, **kwargs) -> "StoreTimezonesModel":
        try:
            data["id"] = str(data.pop("_id"))
        except Exception:
            print(data)
        return cls(*args, **data, **kwargs)


class ReportStatus(str, Enum):
    running = "Running"
    completed = "Completed"
    failed = "Failed"


class ReportStatusModel(MongoBaseModel):
    status: ReportStatus = ReportStatus.running
    createdAt: Optional[datetime] = datetime.now()

    @classmethod
    def from_database(cls, data, *args, **kwargs) -> "ReportStatusModel":
        try:
            data["id"] = str(data.pop("_id"))
        except Exception:
            print(data)
        return cls(*args, **data, **kwargs)
