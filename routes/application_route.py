from flask import Blueprint, jsonify, request
from db.db_connect import get_db

application_route = Blueprint("application_route", __name__)
db = get_db()


# GET /api/application
@application_route.route("/", methods=["GET"])
@application_route.route("", methods=["GET"])
def get_application():
    return jsonify({"message": "GET Application is running MOUAD✅"})


# POST /api/application
@application_route.route("/", methods=["POST"])
@application_route.route("", methods=["POST"])
def create_application():
    try:
        data = request.get_json()

        # Validate data exists
        if not data:
            return jsonify({"message": "No data provided"}), 400

        print(f"Received application data: {data}")
        collection = db["applications"]
        result = collection.insert_one(data)
        print(f"Inserted with ID: {result.inserted_id}")

        data["_id"] = str(result.inserted_id)
        return jsonify(
            {"message": "Application created successfully ✅", "data": data}
        ), 201
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        return jsonify({"message": f"Application creation failed: {str(e)} ❌"}), 500
