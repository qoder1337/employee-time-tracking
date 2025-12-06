from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models.employee import Employee
from src.database.models.shift import Shift
from src.schemas.employee import EmployeeUpdate, EmployeeBase


async def create_employee(db: AsyncSession, employee: EmployeeBase) -> Employee:
    """
    Erstellt einen neuen Mitarbeiter in der Datenbank.
    inkl. automatischen Entpacken der Felder mit **employee.model_dump()
    """
    new_employee = Employee(**employee.model_dump())
    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)
    return new_employee


async def update_employee(
    db: AsyncSession, employee: Employee, employee_update: EmployeeUpdate
) -> Employee:
    """Aktualisiert einen Mitarbeiter mit den übergebenen (optionalen) Feldern"""
    update_data = employee_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)
    return employee


async def delete_employee(db: AsyncSession, employee: Employee) -> None:
    """Löscht einen Mitarbeiter aus der Datenbank"""
    await db.delete(employee)
    await db.commit()


async def get_employee_by_id(db: AsyncSession, employee_id: int) -> Employee | None:
    """Holt einen Mitarbeiter anhand der ID."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    return result.scalar_one_or_none()


async def get_by_employee_number(
    db: AsyncSession, employee_number: str
) -> Employee | None:
    """Holt einen Mitarbeiter anhand der Personalnummer."""
    result = await db.execute(
        select(Employee).where(Employee.employee_number == employee_number)
    )
    return result.scalar_one_or_none()


async def get_all_employees(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Employee]:
    """Holt alle Mitarbeiter mit Pagination."""
    result = await db.execute(
        select(Employee).order_by(Employee.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def calculate_employee_summary(db: AsyncSession, employee_id: int) -> dict:
    """Berechnet Statistiken für einen Mitarbeiter"""

    # Mitarbeiter holen
    employee = await get_employee_by_id(db, employee_id=employee_id)
    if not employee:
        return None

    # Schichten holen
    result = await db.execute(
        select(Shift).where(
            Shift.employee_id == employee_id, Shift.end_time.isnot(None)
        )
    )
    shifts = result.scalars().all()

    if not shifts:
        return {
            "employee_id": employee.id,
            "employee_number": employee.employee_number,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "total_shifts": 0,
            "total_hours_worked": 0.0,
            "average_hours_per_shift": 0.0,
            "total_break_minutes": 0,
            "average_break_per_shift": 0.0,
            "days_worked": 0,
            "first_shift_date": None,
            "last_shift_date": None,
        }

    total_minutes = 0
    total_break = 0
    shift_dates = set()

    for shift in shifts:
        duration = (shift.end_time - shift.start_time).total_seconds() / 60
        net_minutes = duration - shift.break_minutes
        total_minutes += net_minutes
        total_break += shift.break_minutes
        shift_dates.add(shift.start_time.date())

    total_hours = total_minutes / 60

    return {
        "employee_id": employee.id,
        "employee_number": employee.employee_number,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "total_shifts": len(shifts),
        "total_hours_worked": round(total_hours, 2),
        "average_hours_per_shift": round(total_hours / len(shifts), 2),
        "total_break_minutes": total_break,
        "average_break_per_shift": round(total_break / len(shifts), 1),
        "days_worked": len(shift_dates),
        "first_shift_date": min(s.start_time.date() for s in shifts),
        "last_shift_date": max(s.start_time.date() for s in shifts),
    }


async def calculate_all_employees_statistics(db: AsyncSession) -> dict:
    """Berechnet Gesamtstatistiken: über alle Mitarbeiter hinweg"""

    all_employees = await get_all_employees(db, skip=0, limit=10000)
    total_employees = len(all_employees)
    active_employees = len([e for e in all_employees if e.is_active])

    all_shifts_result = await db.execute(
        select(Shift).where(Shift.end_time.isnot(None))
    )
    all_shifts = all_shifts_result.scalars().all()

    # Berechnungen
    total_minutes = 0
    total_break_minutes = 0

    for shift in all_shifts:
        duration = (shift.end_time - shift.start_time).total_seconds() / 60
        net_minutes = duration - shift.break_minutes
        total_minutes += net_minutes
        total_break_minutes += shift.break_minutes

    total_hours = total_minutes / 60

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": total_employees - active_employees,
        "total_shifts": len(all_shifts),
        "total_hours_all": round(total_hours, 2),
        "average_shifts_per_employee": round(len(all_shifts) / total_employees, 1)
        if total_employees > 0
        else 0.0,
        "average_hours_per_employee": round(total_hours / total_employees, 2)
        if total_employees > 0
        else 0.0,
        "total_break_hours": round(total_break_minutes / 60, 2),
    }


# async def calculate_all_employees_statistics(db: AsyncSession) -> dict:
#     """Berechnet Gesamtstatistiken: über alle Mitarbeiter hinweg"""

#     # Alle Mitarbeiter
#     all_employees = await get_all_employees(db, skip=0, limit=10000)
#     total_employees = len(all_employees)
#     active_employees = len([e for e in all_employees if e.is_active])

#     # Alle Schichten
#     all_shifts_result = await db.execute(
#         select(Shift).where(Shift.end_time.isnot(None))
#     )
#     all_shifts = all_shifts_result.scalars().all()

#     if not all_shifts:
#         return {
#             "total_employees": total_employees,
#             "active_employees": active_employees,
#             "inactive_employees": total_employees - active_employees,
#             "total_shifts": 0,
#             "total_hours_all": 0.0,
#             "average_hours_per_employee": 0.0,
#             "average_shifts_per_employee": 0.0,
#             "total_break_hours": 0.0,
#         }

#     # Berechnungen
#     total_minutes = 0
#     total_break_minutes = 0

#     for shift in all_shifts:
#         duration = (shift.end_time - shift.start_time).total_seconds() / 60
#         net_minutes = duration - shift.break_minutes
#         total_minutes += net_minutes
#         total_break_minutes += shift.break_minutes

#     total_hours = total_minutes / 60

#     return {
#         "total_employees": total_employees,
#         "active_employees": active_employees,
#         "inactive_employees": total_employees - active_employees,
#         "total_shifts": len(all_shifts),
#         "total_hours_all": round(total_hours, 2),
#         "average_hours_per_employee": round(total_hours / total_employees, 2)
#         if total_employees > 0
#         else 0.0,
#         "average_shifts_per_employee": round(len(all_shifts) / total_employees, 1)
#         if total_employees > 0
#         else 0.0,
#         "total_break_hours": round(total_break_minutes / 60, 2),
#     }
