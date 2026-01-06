from flask import Blueprint, jsonify, request
from db.db_connect import get_db
from uuid import uuid4
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import base64


class CINResponse(BaseModel):
    firstname: str = Field(..., description="The firstname of the user")
    lastname: str = Field(..., description="The lastname of the user")
    bird_date: str = Field(..., description="The bird date of the user")
    cin_number: str = Field(..., description="The cin number of the user")
    birth_location: str = Field(..., description="The birth location of the user")
    birth_country: str = Field(..., description="The birth country of the user")


load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
MODEL = os.getenv("MODEL")

application_route = Blueprint("application_route", __name__)
db = get_db()


# GET /api/application


@application_route.route("/", methods=["GET"])
def get_application():
    return jsonify({"message": "GET Application is running MOUAD✅"})


@application_route.route("/", methods=["POST"])
def create_application():
    try:
        # Get form data instead of JSON
        data = {}

        # Get regular form fields
        data["exp"] = request.form.get("exp")
        data["role"] = request.form.get("role")
        data["level"] = request.form.get("level")
        data["degree"] = request.form.get("degree")

        # Get skills as array (multiple values with same key)
        skills = request.form.getlist("skills")
        data["skills"] = skills

        # Handle file upload
        file_path = None
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                # Create uploads directory if it doesn't exist
                import os

                os.makedirs("uploads", exist_ok=True)

                # Generate unique filename
                filename = f"{uuid4()}-{file.filename}"
                file_path = f"uploads/{filename}"
                file.save(file_path)
                data["file"] = filename
                print(f"File saved: {filename}")

        # Extract CIN information from the image using OpenAI Vision
        if file_path:
            # Read and encode the image as base64
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            # Determine the image type from the filename
            image_extension = file_path.split(".")[-1].lower()
            mime_type = f"image/{image_extension}"
            if image_extension == "jpg":
                mime_type = "image/jpeg"

            response = client.beta.chat.completions.parse(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting information from ID cards. Extract the information accurately from the CIN card image.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract the following information from this CIN Card image: firstname, lastname, birth_date (bird_date), cin_number, birth_location, and birth_country. Please be accurate and extract exactly what you see.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                response_format=CINResponse,
            )

            # Parse the structured response
            cin_data = response.choices[0].message.parsed
            data["cin"] = {
                "firstname": cin_data.firstname,
                "lastname": cin_data.lastname,
                "birth_date": cin_data.bird_date,
                "cin_number": cin_data.cin_number,
                "birth_location": cin_data.birth_location,
                "birth_country": cin_data.birth_country,
            }
            print("Extracted CIN data: ✅", data["cin"])
        else:
            print("⚠️ No file uploaded, skipping CIN extraction")
        # Validate data exists
        if not data.get("exp") or not data.get("role"):
            return jsonify({"message": "Required fields are missing"}), 400

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
        import traceback

        traceback.print_exc()
        return jsonify({"message": f"Application creation failed: {str(e)} ❌"}), 500
