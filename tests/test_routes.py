"""API and model tests."""

import pytest

from service import create_app
from service.models import Customer, CustomerRepository


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "CORS_ORIGINS": "https://example.com"})
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def customer_payload():
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "address": "1 Analytical Engine Way",
    }


def test_customer_model_serializes_to_dict():
    customer = Customer("Ada", "Lovelace", "ada@example.com", "London")
    result = customer.to_dict()
    assert result["id"] == str(customer.id)
    assert result["email"] == "ada@example.com"


def test_repository_crud():
    repository = CustomerRepository()
    customer = repository.add(Customer("Ada", "Lovelace", "ada@example.com", "London"))
    assert repository.get(customer.id) == customer
    repository.update(customer.id, {"address": "Paris"})
    assert repository.get(customer.id).address == "Paris"
    assert repository.update("missing", {"address": "Rome"}) is None
    assert repository.delete(customer.id)
    assert repository.get(customer.id) is None
    repository.clear()


def test_customer_crud_api(client, customer_payload):
    response = client.post("/api/customers", json=customer_payload)
    assert response.status_code == 201
    customer = response.get_json()
    customer_id = customer["id"]

    assert client.get("/api/customers").get_json() == [customer]
    assert client.get(f"/api/customers/{customer_id}").get_json() == customer

    updated = {**customer_payload, "address": "Paris"}
    response = client.put(f"/api/customers/{customer_id}", json=updated)
    assert response.status_code == 200
    assert response.get_json()["address"] == "Paris"

    response = client.delete(f"/api/customers/{customer_id}")
    assert response.status_code == 204
    assert client.get(f"/api/customers/{customer_id}").status_code == 404


def test_patch_and_validation(client, customer_payload):
    customer_id = client.post("/api/customers", json=customer_payload).get_json()["id"]
    response = client.patch(f"/api/customers/{customer_id}", json={"last_name": "Byron"})
    assert response.status_code == 200
    assert response.get_json()["last_name"] == "Byron"
    assert client.post("/api/customers", json={"email": "invalid"}).status_code == 400
    assert client.post("/api/customers", json={"unknown": "value"}).status_code == 400
    assert client.post("/api/customers", json={"first_name": 1}).status_code == 400
    assert client.post("/api/customers", data="not-json",
                       content_type="application/json").status_code == 400
    assert client.put(f"/api/customers/{customer_id}", json={"email": "only"}).status_code == 400
    assert client.patch("/api/customers/00000000-0000-0000-0000-000000000000",
                        json={"last_name": "Nobody"}).status_code == 404
    assert client.delete("/api/customers/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/api/customers/not-a-uuid").status_code == 404


def test_security_headers_and_cors(client):
    response = client.get("/health", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Content-Security-Policy"] == "default-src 'none'"
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
