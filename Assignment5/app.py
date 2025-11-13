from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = Path(__file__).resolve().parent / "truckinglist.json"
REQUIRED_FIELDS = {"Company", "Services", "Hubs", "Revenue", "HomePage", "Logo"}


def load_data() -> Dict[str, Any]:
    """Load company dataset from disk."""
    if not DATA_FILE.exists():
        return {"companies": []}

    try:
        with DATA_FILE.open(encoding="utf-8") as fp:
            return json.load(fp)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON structure: {exc}") from exc


def save_data(data: Dict[str, Any]) -> None:
    """Persist dataset back to disk."""
    with DATA_FILE.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)


def find_company(companies: List[Dict[str, Any]], name: str) -> Dict[str, Any] | None:
    """Return company dict matching name, case insensitive."""
    name_lower = name.strip().lower()
    for company in companies:
        if company.get("Company", "").strip().lower() == name_lower:
            return company
    return None


@app.route("/")
def index() -> str:
    return (
        """
        <h2>Trucking Company API</h2>
        <p>This is a RESTful API for managing trucking company data.</p>
        <p>Available endpoints:</p>
        <ul>
            <li>GET /companies</li>
            <li>GET /companies/&lt;name&gt;</li>
            <li>POST /companies</li>
            <li>PUT /companies/&lt;name&gt;</li>
            <li>DELETE /companies/&lt;name&gt;</li>
        </ul>
        """
    )


@app.route("/companies", methods=["GET"])
def get_all_companies():
    """Return all companies from dataset."""
    try:
        data = load_data()
        companies = data.get("companies", [])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify(companies), HTTPStatus.OK


@app.route("/companies/<string:name>", methods=["GET"])
def get_company(name: str):
    try:
        data = load_data()
        companies = data.get("companies", [])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    company = find_company(companies, name)
    if not company:
        return jsonify({"error": f"Company '{name}' not found"}), HTTPStatus.NOT_FOUND

    return jsonify(company), HTTPStatus.OK


@app.route("/companies", methods=["POST"])
def add_company():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Malformed JSON"}), HTTPStatus.BAD_REQUEST

    missing_fields = REQUIRED_FIELDS - payload.keys()
    if missing_fields:
        return (
            jsonify({"error": f"Missing required fields: {', '.join(sorted(missing_fields))}"}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        data = load_data()
        companies = data.setdefault("companies", [])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    if find_company(companies, payload.get("Company", "")):
        return (
            jsonify({"error": f"Company '{payload['Company']}' already exists"}),
            HTTPStatus.CONFLICT,
        )

    companies.append(payload)
    save_data(data)

    return jsonify(payload), HTTPStatus.CREATED


@app.route("/companies/<string:name>", methods=["PUT"])
def update_company(name: str):
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    updates = request.get_json(silent=True)
    if updates is None:
        return jsonify({"error": "Malformed JSON"}), HTTPStatus.BAD_REQUEST

    if "Company" in updates and updates["Company"].strip().lower() != name.strip().lower():
        return jsonify({"error": "Company name in payload does not match URL"}), HTTPStatus.BAD_REQUEST

    try:
        data = load_data()
        companies = data.get("companies", [])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    company = find_company(companies, name)
    if not company:
        return jsonify({"error": f"Company '{name}' not found"}), HTTPStatus.NOT_FOUND

    company.update(updates)
    save_data(data)

    return jsonify(company), HTTPStatus.OK


@app.route("/companies/<string:name>", methods=["DELETE"])
def delete_company(name: str):
    try:
        data = load_data()
        companies = data.get("companies", [])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    company = find_company(companies, name)
    if not company:
        return jsonify({"error": f"Company '{name}' not found"}), HTTPStatus.NOT_FOUND

    companies.remove(company)
    save_data(data)

    return jsonify({"message": f"Company '{name}' deleted"}), HTTPStatus.NO_CONTENT


@app.errorhandler(404)
def not_found(error):  # type: ignore[override]
    return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND


@app.errorhandler(400)
def bad_request(error):  # type: ignore[override]
    return jsonify({"error": "Bad request"}), HTTPStatus.BAD_REQUEST


@app.errorhandler(500)
def server_error(error):  # type: ignore[override]
    return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
