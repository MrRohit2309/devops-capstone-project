"""REST routes for customer accounts."""

from uuid import UUID

from flask import Blueprint, current_app, jsonify, request

from .models import Customer

CUSTOMER_FIELDS = ("first_name", "last_name", "email", "address")
REQUIRED_FIELDS = CUSTOMER_FIELDS
customers_blueprint = Blueprint("customers", __name__)


def _repository():
    return current_app.extensions["customer_repository"]


def _parse_customer_id(value: str):
    try:
        return UUID(value)
    except ValueError:
        return None


def _validate_payload(payload, partial=False):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."
    unknown = set(payload) - set(CUSTOMER_FIELDS)
    if unknown:
        return f"Unknown fields: {', '.join(sorted(unknown))}."
    required = set() if partial else set(REQUIRED_FIELDS)
    missing = required - set(payload)
    if missing:
        return f"Missing required fields: {', '.join(sorted(missing))}."
    for field in payload:
        if not isinstance(payload[field], str) or not payload[field].strip():
            return f"{field} must be a non-empty string."
    return None


@customers_blueprint.get("/customers")
def list_customers():
    return jsonify([customer.to_dict() for customer in _repository().list()])


@customers_blueprint.post("/customers")
def create_customer():
    payload = request.get_json(silent=True)
    error = _validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400
    customer = _repository().add(Customer(**payload))
    return jsonify(customer.to_dict()), 201


@customers_blueprint.get("/customers/<customer_id>")
def get_customer(customer_id):
    parsed_id = _parse_customer_id(customer_id)
    customer = _repository().get(parsed_id) if parsed_id else None
    if customer is None:
        return jsonify({"error": "Customer not found."}), 404
    return jsonify(customer.to_dict())


@customers_blueprint.put("/customers/<customer_id>")
def update_customer(customer_id):
    parsed_id = _parse_customer_id(customer_id)
    payload = request.get_json(silent=True)
    error = _validate_payload(payload, partial=False)
    if error:
        return jsonify({"error": error}), 400
    customer = _repository().update(parsed_id, payload) if parsed_id else None
    if customer is None:
        return jsonify({"error": "Customer not found."}), 404
    return jsonify(customer.to_dict())


@customers_blueprint.patch("/customers/<customer_id>")
def patch_customer(customer_id):
    parsed_id = _parse_customer_id(customer_id)
    payload = request.get_json(silent=True)
    error = _validate_payload(payload, partial=True)
    if error:
        return jsonify({"error": error}), 400
    customer = _repository().update(parsed_id, payload) if parsed_id else None
    if customer is None:
        return jsonify({"error": "Customer not found."}), 404
    return jsonify(customer.to_dict())


@customers_blueprint.delete("/customers/<customer_id>")
def delete_customer(customer_id):
    parsed_id = _parse_customer_id(customer_id)
    deleted = _repository().delete(parsed_id) if parsed_id else False
    if not deleted:
        return jsonify({"error": "Customer not found."}), 404
    return "", 204
