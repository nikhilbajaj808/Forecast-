from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

OPENWEATHER_KEY = "8750edaaa47da6361ceabe52b9242539"

@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/get_weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    city = data.get("city")
    date_str = data.get("date")

    if not city or not date_str:
        return jsonify({"error": "Missing city or date"}), 400

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != "200":
        return jsonify({"error": "City not found"}), 404

    today_date = datetime.strptime(date_str, "%Y-%m-%d")
    forecast_list = []
    seen_times = set()

    for item in res["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        if today_date <= dt <= today_date + timedelta(days=3):
            dt_str = dt.strftime("%Y-%m-%d %H:%M")
            if dt_str not in seen_times:
                seen_times.add(dt_str)
                forecast_list.append({
                    "date": dt_str,
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "temperature": round(item["main"]["temp"], 1),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": round(item["wind"]["speed"], 1),
                    "probability": round(item.get("pop", 0) * 100, 1)
                })

    today_weather = forecast_list[0] if forecast_list else None
    return jsonify({"today": today_weather, "forecast": forecast_list})

if __name__ == "__main__":
    app.run(debug=True)
