from flask import Flask, jsonify
import hashlib

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({"service": "Supporting", "framework": "Flask", "status": "running"})

@app.route("/api/hash/<text>")
def hash_endpoint(text):
    result = hashlib.sha256(text.encode()).hexdigest()
    return jsonify({
        "request": text,
        "result": result
    })

@app.route("/api/dashboard")
def dashboard():
    return jsonify({
        "request": "dashboard",
        "result": {
            "categories": ["Янв", "Фев", "Мар", "Апр"],
            "series": [
                {"name": "Бронирования", "data": [12, 19, 8, 24]},
                {"name": "Заказы", "data": [45, 60, 30, 55]}
            ]
        }
    })

@app.route("/api/about")
def about():
    return jsonify({
        "request": "about",
        "result": {
            "project": "Bar Web App",
            "team": 4,
            "stack": "FastAPI + Flask + PostgreSQL"
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)