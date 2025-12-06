from fastapi import APIRouter, HTTPException, Query, status
from src.schemas.shift import ShiftCreate, ShiftRead, ShiftUpdate
from src.crud import validation
from src.crud import shift as shift_crud
from src.crud import employee as employee_crud
from src.database import DBSessionDep_local

shift_route = APIRouter(prefix="/shifts", tags=["SHIFTS ROUTE"])


@shift_route.post("/", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
async def create_shift(shift: ShiftCreate, db: DBSessionDep_local):
    """
    Neue Schicht erfassen
    Prüft, ob Mitarbeiter-ID existiert und auf Schichtüberlappung

    Returns: Neue Schicht
    """

    # Mitarbeiter existiert?
    employee = await employee_crud.get_employee_by_id(db, employee_id=shift.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mitarbeiter mit ID {shift.employee_id} nicht gefunden",
        )

    # Alle Validierungen
    await validation.validate_shift_constraints(
        db=db,
        employee_id=shift.employee_id,
        start_time=shift.start_time,
        end_time=shift.end_time,
        break_minutes=shift.break_minutes,
    )

    new_shift = await shift_crud.create_shift(db=db, shift=shift)
    return new_shift


@shift_route.get("/{shift_id}", response_model=ShiftRead)
async def get_shift(shift_id: int, db: DBSessionDep_local):
    """Schicht via ID abrufen"""
    shift = await shift_crud.get_shift_by_id(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schicht nicht gefunden"
        )
    return shift


@shift_route.get("/", response_model=list[ShiftRead])
async def list_shifts(
    db: DBSessionDep_local,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: int | None = None,
):
    """Alle Schichten auflisten (optional gefiltert nach employee_id)"""
    if employee_id:
        shifts = await shift_crud.get_shifts_by_employee(
            db, employee_id=employee_id, skip=skip, limit=limit
        )
    else:
        shifts = await shift_crud.get_all_shifts(db, skip=skip, limit=limit)
    return shifts


@shift_route.patch("/{shift_id}", response_model=ShiftRead)
async def update_shift(
    shift_id: int, shift_update: ShiftUpdate, db: DBSessionDep_local
):
    """Schicht aktualisieren"""
    shift = await shift_crud.get_shift_by_id(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schicht nicht gefunden"
        )

    # Wenn Zeiten geändert werden, prüfe auf Überlappung
    new_start = shift_update.start_time or shift.start_time
    new_end = shift_update.end_time or shift.end_time
    new_break = (
        shift_update.break_minutes
        if shift_update.break_minutes is not None
        else shift.break_minutes
    )

    # Alle Validierungen in einer Funktion
    await validation.validate_shift_constraints(
        db=db,
        employee_id=shift.employee_id,
        start_time=new_start,
        end_time=new_end,
        break_minutes=new_break,
        exclude_shift_id=shift_id,
    )

    updated_shift = await shift_crud.update_shift(
        db=db, shift=shift, shift_update=shift_update
    )
    return updated_shift


@shift_route.delete("/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift(shift_id: int, db: DBSessionDep_local):
    """Schicht löschen"""
    shift = await shift_crud.get_shift_by_id(db, shift_id=shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schicht nicht gefunden"
        )
    await shift_crud.delete_shift(db=db, shift=shift)
