from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.shift import Shift
from src.schemas.shift import ShiftCreate, ShiftUpdate


async def create_shift(db: AsyncSession, shift: ShiftCreate) -> Shift:
    """Erstellt eine neue Schicht."""
    new_shift = Shift(**shift.model_dump())
    db.add(new_shift)
    await db.commit()
    await db.refresh(new_shift)
    return new_shift


async def get_shift_by_id(db: AsyncSession, shift_id: int) -> Shift | None:
    """Holt eine Schicht anhand der ID."""
    result = await db.execute(select(Shift).where(Shift.id == shift_id))
    return result.scalar_one_or_none()


async def get_all_shifts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Shift]:
    """Holt alle Schichten mit Pagination."""
    result = await db.execute(
        select(Shift).order_by(Shift.start_time.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_shifts_by_employee(
    db: AsyncSession, employee_id: int, skip: int = 0, limit: int = 100
) -> list[Shift]:
    """Holt alle Schichten eines bestimmten Mitarbeiters."""
    result = await db.execute(
        select(Shift)
        .where(Shift.employee_id == employee_id)
        .order_by(Shift.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_shift(
    db: AsyncSession, shift: Shift, shift_update: ShiftUpdate
) -> Shift:
    """Aktualisiert eine Schicht."""
    update_data = shift_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shift, field, value)
    await db.commit()
    await db.refresh(shift)
    return shift


async def delete_shift(db: AsyncSession, shift: Shift) -> None:
    """Löscht eine Schicht."""
    await db.delete(shift)
    await db.commit()
