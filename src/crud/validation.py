from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import date, datetime, timedelta
from src.database.models.shift import Shift


async def get_total_hours_on_date(
    db: AsyncSession,
    employee_id: int,
    shift_date: date,
    exclude_shift_id: int | None = None,
) -> float:
    """
    VALIDIERUNG 3
    Berechnet die Gesamtarbeitszeit an einem bestimmten Tag.
    Berücksichtigt auch Nachtschichten, die über Mitternacht gehen.
    Returns: Stunden als float
    """
    day_start = datetime.combine(shift_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(Shift).where(
            Shift.employee_id == employee_id,
            Shift.end_time.isnot(None),
            # Schicht überlappt mit dem Ziel-Tag
            Shift.start_time < day_end,
            Shift.end_time > day_start,
        )
    )
    shifts = result.scalars().all()

    total_minutes = 0
    for shift in shifts:
        if exclude_shift_id and shift.id == exclude_shift_id:
            continue

        # Nur den Teil berechnen, der in den Ziel-Tag fällt
        effective_start = max(shift.start_time, day_start)
        effective_end = min(shift.end_time, day_end)

        duration_minutes = (effective_end - effective_start).total_seconds() / 60

        # Pause anteilig verteilen (vereinfachte Annahme: Pause gleichmäßig über Schicht)
        total_shift_minutes = (shift.end_time - shift.start_time).total_seconds() / 60
        pause_ratio = (
            duration_minutes / total_shift_minutes if total_shift_minutes > 0 else 0
        )
        effective_pause = shift.break_minutes * pause_ratio

        total_minutes += duration_minutes - effective_pause

    return total_minutes / 60


async def count_consecutive_workdays(
    db: AsyncSession, employee_id: int, shift_date: date
) -> int:
    """
    VALIDIERUNG 2
    Zählt aufeinanderfolgende Arbeitstage VOR dem gegebenen Datum.
    Returns: Anzahl der Tage (0-5+)
    """

    MAX_DAYS = 5
    consecutive_days = 0
    current_date = shift_date - timedelta(days=1)

    for _ in range(MAX_DAYS):
        result = await db.execute(
            select(Shift)
            .where(
                Shift.employee_id == employee_id,
                Shift.start_time >= current_date,
                Shift.start_time < current_date + timedelta(days=1),
            )
            .limit(1)
        )

        if result.scalar_one_or_none():
            consecutive_days += 1
            current_date -= timedelta(days=1)
        else:
            break

    return consecutive_days


async def check_overlapping_shifts(
    db: AsyncSession,
    employee_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_shift_id: int | None = None,
) -> Shift | None:
    """
    VALIDIERUNG 1
    Prüft ob es überlappende Schichten für einen Mitarbeiter gibt.
    exclude_shift_id kommt zum Einsatz wenn man eine bereits existierende Schiht ändenr muss

    Returns: Die überlappende Schicht oder None
    """
    query = select(Shift).where(
        Shift.employee_id == employee_id,
        Shift.end_time.isnot(None),
        or_(
            # Neue Schicht startet während existierender Schicht
            (Shift.start_time <= start_time) & (Shift.end_time > start_time),
            # Neue Schicht endet während existierender Schicht
            (Shift.start_time < end_time) & (Shift.end_time >= end_time),
            # Neue Schicht umschließt existierende Schicht komplett
            (Shift.start_time >= start_time) & (Shift.end_time <= end_time),
        ),
    )

    if exclude_shift_id:
        query = query.where(Shift.id != exclude_shift_id)

    result = await db.execute(query)
    # return result.scalar_one_or_none()
    return result.scalars().first()


async def validate_shift_constraints(
    db: AsyncSession,
    employee_id: int,
    start_time: datetime,
    end_time: datetime,
    break_minutes: int,
    exclude_shift_id: int | None = None,
) -> None:
    """
    MAIN VALDIDATION:
    Validiert alle Business-Rules für eine Schicht.
    Raises HTTPException bei Verletzung.
    """
    shift_date = start_time.date()

    # 1. Überlappung prüfen
    overlap = await check_overlapping_shifts(
        db,
        employee_id=employee_id,
        start_time=start_time,
        end_time=end_time,
        exclude_shift_id=exclude_shift_id,
    )
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Schicht überschneidet sich mit Schicht ID {overlap.id}",
        )

    # 2. Aufeinanderfolgende Arbeitstage prüfen
    if exclude_shift_id is None:
        consecutive = await count_consecutive_workdays(
            db, employee_id=employee_id, shift_date=shift_date
        )
        if consecutive >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximale Anzahl aufeinanderfolgender Arbeitstage (5) erreicht. "
                f"Bereits {consecutive} Tage gearbeitet.",
            )

    # 3. Tagesarbeitszeit prüfen
    existing_hours = await get_total_hours_on_date(
        db,
        employee_id=employee_id,
        shift_date=shift_date,
        exclude_shift_id=exclude_shift_id,
    )

    new_hours = ((end_time - start_time).total_seconds() / 3600) - (break_minutes / 60)
    total_hours = existing_hours + new_hours

    if total_hours > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximale Tagesarbeitszeit (10h) überschritten. "
            f"gesamt: {total_hours:.1f}h",
        )
