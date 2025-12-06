import pytest
from httpx import AsyncClient
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_create_shift(client: AsyncClient):
    """Teste Schicht erfassen"""

    emp_response = await client.post(
        "/employees/",
        json={
            "employee_number": "E001",
            "first_name": "Max",
            "last_name": "Mustermann",
            "is_active": True,
        },
    )
    employee_id = emp_response.json()["id"]

    # Schicht anlegen
    now = datetime.now(timezone.utc)
    shift_data = {
        "employee_id": employee_id,
        "start_time": now.replace(hour=8, minute=0).isoformat(),
        "end_time": now.replace(hour=16, minute=0).isoformat(),
        "break_minutes": 30,
    }

    response = await client.post("/shifts/", json=shift_data)
    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["break_minutes"] == 30


@pytest.mark.asyncio
async def test_shift_end_before_start_validation(client: AsyncClient):
    """Teste Validierung: Schichtende vor Schichtbeginn"""
    # Mitarbeiter anlegen
    emp_response = await client.post(
        "/employees/",
        json={
            "employee_number": "E001",
            "first_name": "Max",
            "last_name": "Mustermann",
            "is_active": True,
        },
    )
    employee_id = emp_response.json()["id"]

    # Ungültige Schicht (Ende vor Start)
    now = datetime.now(timezone.utc)
    shift_data = {
        "employee_id": employee_id,
        "start_time": now.replace(hour=16, minute=0).isoformat(),
        "end_time": now.replace(hour=8, minute=0).isoformat(),
        "break_minutes": 30,
    }

    response = await client.post("/shifts/", json=shift_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_overlapping_shifts_validation(client: AsyncClient):
    """Teste Validierung: Überlappende Schichten"""
    # Mitarbeiter anlegen
    emp_response = await client.post(
        "/employees/",
        json={
            "employee_number": "E001",
            "first_name": "Max",
            "last_name": "Mustermann",
            "is_active": True,
        },
    )
    employee_id = emp_response.json()["id"]

    now = datetime.now(timezone.utc)

    # Erste Schicht: 8-16 Uhr
    shift1 = {
        "employee_id": employee_id,
        "start_time": now.replace(hour=8, minute=0).isoformat(),
        "end_time": now.replace(hour=16, minute=0).isoformat(),
        "break_minutes": 30,
    }
    response1 = await client.post("/shifts/", json=shift1)
    assert response1.status_code == 201

    # Zweite Schicht: 14-18 Uhr (überlappt!)
    shift2 = {
        "employee_id": employee_id,
        "start_time": now.replace(hour=14, minute=0).isoformat(),
        "end_time": now.replace(hour=18, minute=0).isoformat(),
        "break_minutes": 30,
    }
    response2 = await client.post("/shifts/", json=shift2)
    assert response2.status_code == 409
