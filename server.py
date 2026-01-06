from flask import Flask, request, jsonify, Blueprint, render_template
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from db.db_connect import get_db
from routes.application_route import application_route

load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)


get_db()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


app.register_blueprint(application_route, url_prefix="/api/application")

if __name__ == "__main__":
    print(
        f"Server is running on port {os.getenv('PORT')} ✅ in this link http://localhost:{os.getenv('PORT')}"
    )

    app.run(host="0.0.0.0", debug=True, port=int(os.getenv("PORT")))
