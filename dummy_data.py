import asyncio
from datetime import datetime, timedelta, timezone
from src.database import sessionmanager_local, Base
from src.database.models.employee import Employee
from src.database.models.shift import Shift


async def seed_database():
    """Füllt die Datenbank mit Testdaten"""

    # Tabellen erstellen (falls nicht vorhanden)
    async with sessionmanager_local.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmanager_local.session() as db:
        # 1. Mitarbeiter anlegen
        employees = [
            Employee(
                employee_number="E001",
                first_name="Max",
                last_name="Mustermann",
                is_active=True,
            ),
            Employee(
                employee_number="E002",
                first_name="Anna",
                last_name="Schmidt",
                is_active=True,
            ),
            Employee(
                employee_number="E003",
                first_name="Tom",
                last_name="Müller",
                is_active=True,
            ),
            Employee(
                employee_number="E004",
                first_name="Lisa",
                last_name="Weber",
                is_active=False,
            ),
        ]

        db.add_all(employees)
        await db.commit()

        # IDs aktualisieren
        for emp in employees:
            await db.refresh(emp)

        # 2. Schichten für die letzten 7 Tage anlegen
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        shifts = []
        for i in range(7):
            shift_date = today - timedelta(days=i)

            # Max: Normale 8h-Schicht
            shifts.append(
                Shift(
                    employee_id=employees[0].id,
                    start_time=shift_date.replace(hour=8),
                    end_time=shift_date.replace(hour=16),
                    break_minutes=30,
                )
            )

            # Anna: Teilzeit 6h-Schicht (nur jeden 2. Tag)
            if i % 2 == 0:
                shifts.append(
                    Shift(
                        employee_id=employees[1].id,
                        start_time=shift_date.replace(hour=9),
                        end_time=shift_date.replace(hour=15),
                        break_minutes=30,
                    )
                )

            # Tom: Nachtschicht (nur die letzten 3 Tage)
            if i < 3:
                shifts.append(
                    Shift(
                        employee_id=employees[2].id,
                        start_time=shift_date.replace(hour=22),
                        end_time=(shift_date + timedelta(days=1)).replace(hour=6),
                        break_minutes=45,
                    )
                )

        db.add_all(shifts)
        await db.commit()

        print(f"✅ {len(employees)} Mitarbeiter angelegt")
        print(f"✅ {len(shifts)} Schichten angelegt")
        print("\nMitarbeiter:")
        for emp in employees:
            print(f"  - {emp.employee_number}: {emp.first_name} {emp.last_name}")


async def cleanup():
    """Schließt DB-Verbindungen"""
    await sessionmanager_local.close()


if __name__ == "__main__":
    print("🌱 Seeding Datenbank...")
    asyncio.run(seed_database())
    print("✨ Fertig!")
