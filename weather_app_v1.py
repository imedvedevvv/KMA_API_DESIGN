from datetime import datetime, timezone
import json

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

def get_weather(location: str, date: str):
    url_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

    url = f"{url_base_url}/{location}/{date}?key={RSA_KEY}"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/weather", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requester_name = ""
    if json_data.get("requester_name"):
        requester_name = json_data.get("requester_name")

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")

    date = ""
    if json_data.get("date"):
        date = json_data.get("date")

    weather = get_weather(location, date)

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')

    result = {
        "requester_name": requester_name,
        "timestamp": timestamp,
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result
