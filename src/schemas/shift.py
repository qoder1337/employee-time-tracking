from pydantic import BaseModel, model_validator, field_validator, ConfigDict
from datetime import datetime, date, timezone


class ShiftCreate(BaseModel):
    """
    Eingabe Validierung
    """

    employee_id: int
    start_time: datetime
    end_time: datetime
    break_minutes: int = 0

    @field_validator("start_time", "end_time")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    # VALIDATION 4
    @model_validator(mode="after")
    def check_times(self) -> "ShiftCreate":
        if self.end_time is not None and self.start_time >= self.end_time:
            raise ValueError("Schichtende muss zeitlich nach Schichtbeginn liegen.")
        return self


class ShiftUpdate(BaseModel):
    """
    Partial Update für PATCH-Requests
    """

    start_time: datetime | None = None
    end_time: datetime | None = None
    break_minutes: int | None = None

    # VALIDATION 4
    @model_validator(mode="after")
    def check_times(self) -> "ShiftUpdate":
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("Schichtende muss zeitlich nach Schichtbeginn liegen.")
        return self


class ShiftRead(ShiftCreate):
    """
    Ausgabe der Schichtdaten
    shift_date ist aus der hybrid_property des DB-Modells
    """

    id: int
    shift_date: date

    model_config = ConfigDict(from_attributes=True)
