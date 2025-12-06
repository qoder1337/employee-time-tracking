import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient):
    """Teste Mitarbeiter anlegen"""
    response = await client.post(
        "/employees/",
        json={
            "employee_number": "E999",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["employee_number"] == "E999"
    assert data["first_name"] == "Test"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_employee_not_found(client: AsyncClient):
    """Teste 404 bei nicht existierendem Mitarbeiter"""
    response = await client.get("/employees/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient):
    """Teste Mitarbeiter-Liste"""
    # Mitarbeiter anlegen
    await client.post(
        "/employees/",
        json={
            "employee_number": "E001",
            "first_name": "Max",
            "last_name": "Mustermann",
            "is_active": True,
        },
    )

    # Liste abrufen
    response = await client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_duplicate_employee_number(client: AsyncClient):
    """Teste, ob doppelte Personalnummern abgelehnt werden"""
    employee_data = {
        "employee_number": "E123",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
    }

    # Ersten Mitarbeiter anlegen
    response1 = await client.post("/employees/", json=employee_data)
    assert response1.status_code == 201

    # Zweiten mit gleicher Nummer versuchen
    response2 = await client.post("/employees/", json=employee_data)
    assert response2.status_code == 409  # Conflict
