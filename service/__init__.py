"""Application factory for the Customer Accounts service."""

from flask import Flask, jsonify
from flask_cors import CORS

from .models import CustomerRepository
from .routes import customers_blueprint


def create_app(test_config=None):
    """Create and configure the Flask application."""
    application = Flask(__name__)
    application.config.from_mapping(
        TESTING=False,
        CORS_ORIGINS="*",
    )
    if test_config:
        application.config.update(test_config)

    application.extensions["customer_repository"] = CustomerRepository()
    CORS(application, resources={r"/*": {"origins": application.config["CORS_ORIGINS"]}})
    application.register_blueprint(customers_blueprint, url_prefix="/api")
    application.register_blueprint(customers_blueprint, url_prefix="", name="customers_root")

    @application.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response

    @application.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return application


app = create_app()
