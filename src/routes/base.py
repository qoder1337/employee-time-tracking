from fastapi import APIRouter
from src.database import DBSessionDep_local
from src.schemas.employee import EmployeeStatistics
from src.crud import employee as employee_crud


base_route = APIRouter(tags=["BASE ROUTE"])


@base_route.get("/")
async def root():
    return {"message": "HELLO 'Employee Time Tracking' WORLD"}


@base_route.get("/statistics", response_model=EmployeeStatistics)
async def get_all_employees_statistics(db: DBSessionDep_local):
    """Gesamtstatistik über alle Mitarbeiter"""
    stats = await employee_crud.calculate_all_employees_statistics(db)
    return stats
