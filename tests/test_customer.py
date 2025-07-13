import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from flasx.main import app
from sqlmodel import SQLModel

from flasx.models import get_session

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from base import session, engine, client


@pytest.fixture
def customer_data():
    return {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}


@pytest.mark.asyncio
async def test_create_customer(client, customer_data):
    response = await client.post("/v1/customers", json=customer_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_customers(client):
    response = await client.get("/v1/customers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_customer_by_id(client, customer_data):
    # Create a customer first
    create_resp = await client.post("/v1/customers", json=customer_data)
    customer_id = create_resp.json()["id"]

    # Retrieve the customer
    response = await client.get(f"/v1/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id


@pytest.mark.asyncio
async def test_update_customer(client, customer_data):
    # Create a customer first
    create_resp = await client.post("/v1/customers", json=customer_data)
    customer_id = create_resp.json()["id"]

    updated_data = customer_data.copy()
    updated_data["name"] = "Jane Doe"

    response = await client.put(f"/v1/customers/{customer_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_delete_customer(client, customer_data):
    # Create a customer first
    create_resp = await client.post("/v1/customers", json=customer_data)
    customer_id = create_resp.json()["id"]

    response = await client.delete(f"/v1/customers/{customer_id}")
    assert response.status_code == 204

    # Ensure customer is deleted
    get_resp = await client.get(f"/v1/customers/{customer_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_activate_customer(client, customer_data):
    # Create a customer first
    create_resp = await client.post("/v1/customers", json=customer_data)
    customer_id = create_resp.json()["id"]

    response = await client.patch(f"/v1/customers/{customer_id}/activate")
    assert response.status_code == 200
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_deactivate_customer(client, customer_data):
    # Create a customer first
    create_resp = await client.post("/v1/customers", json=customer_data)
    customer_id = create_resp.json()["id"]

    response = await client.patch(f"/v1/customers/{customer_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_get_customer_by_email(client, customer_data):
    # Create a customer first
    await client.post("/v1/customers", json=customer_data)

    # Get by email
    response = await client.get(f"/v1/customers/email/{customer_data['email']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == customer_data["email"]


@pytest.mark.asyncio
async def test_create_customer_duplicate_email(client, customer_data):
    # Create a customer first
    await client.post("/v1/customers", json=customer_data)

    # Try to create another with same email
    response = await client.post("/v1/customers", json=customer_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
