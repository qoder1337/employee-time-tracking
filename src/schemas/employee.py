from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class EmployeeBase(BaseModel):
    """
    Input Schema
    """

    employee_number: str
    first_name: str
    last_name: str
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    """
    Partial Update für PATCH-Requests
    """

    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


class EmployeeRead(EmployeeBase):
    """
    Output Schema
    """

    id: int
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class EmployeeSummary(BaseModel):
    """
    Auswertung für einen Mitarbeiter
    """

    # Basis-Info
    employee_id: int
    employee_number: str
    first_name: str
    last_name: str

    # Statistiken
    total_shifts: int
    total_hours_worked: float
    average_hours_per_shift: float
    total_break_minutes: int
    average_break_per_shift: float
    days_worked: int
    first_shift_date: date | None
    last_shift_date: date | None


class EmployeeStatistics(BaseModel):
    """
    Statistik für alle Mitarbeiter
    """

    total_employees: int
    active_employees: int
    inactive_employees: int
    total_shifts: int
    total_hours_all: float
    average_shifts_per_employee: float
    average_hours_per_employee: float
    total_break_hours: float
