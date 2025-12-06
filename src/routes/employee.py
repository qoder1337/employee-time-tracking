from fastapi import APIRouter, HTTPException, Query, status
from src.database import DBSessionDep_local
from src.schemas.employee import (
    EmployeeBase,
    EmployeeRead,
    EmployeeUpdate,
    EmployeeSummary,
)
from src.crud import employee as employee_crud


employee_route = APIRouter(prefix="/employees", tags=["EMPLOYEES ROUTE"])


@employee_route.post(
    "/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED
)
async def create_employee(employee: EmployeeBase, db: DBSessionDep_local):
    """
    Neuen Mitarbeiter anlegen
    inkl. initialer Prüfung, ob Personalnummer bereits existiert
    """

    existing = await employee_crud.get_by_employee_number(db, employee.employee_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mitarbeiter mit Personalnummer {employee.employee_number} existiert bereits",
        )

    new_employee = await employee_crud.create_employee(db=db, employee=employee)
    return new_employee


@employee_route.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: int, db: DBSessionDep_local):
    """Mitarbeiter via DB-ID finden"""
    employee = await employee_crud.get_employee_by_id(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden"
        )
    return employee


@employee_route.get("/{employee_id}/summary", response_model=EmployeeSummary)
async def get_employee_summary(employee_id: int, db: DBSessionDep_local):
    """Auswertung/Statistik für einen Mitarbeiter"""
    summary = await employee_crud.calculate_employee_summary(
        db, employee_id=employee_id
    )
    if summary is None:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    return summary


@employee_route.get("/", response_model=list[EmployeeRead])
async def list_employees(
    db: DBSessionDep_local,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Alle Mitarbeiter auflisten (mit Pagination)
    https://fastapi.tiangolo.com/tutorial/query-params-str-validations/
    """
    employees = await employee_crud.get_all_employees(db, skip=skip, limit=limit)
    return employees


@employee_route.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: int, employee_update: EmployeeUpdate, db: DBSessionDep_local
):
    """Mitarbeiter aktualisieren (Partial Update)"""
    employee = await employee_crud.get_employee_by_id(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden"
        )

    updated_employee = await employee_crud.update_employee(
        db=db, employee=employee, employee_update=employee_update
    )
    return updated_employee


@employee_route.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, db: DBSessionDep_local):
    """Mitarbeiter löschen"""
    employee = await employee_crud.get_employee_by_id(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden"
        )

    await employee_crud.delete_employee(db=db, employee=employee)
