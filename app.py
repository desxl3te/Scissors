from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from app.core.config import settings
from app.core.files import read_json
import app.db.repository as repository
from app.storage.support_store import support_messages_count

# Flask приложение для дашборда администратора
# На отдельных портах от основного API
def _build_weekday_chart(raw_rows: list[dict]) -> dict:
    config = read_json(settings.dashboard_config_path, {"weekday_order": []})
    weekday_totals = {row["weekday"]: row["total"] for row in raw_rows}
    labels = []
    data = []

    for item in config.get("weekday_order", []):
        labels.append(item["label"])
        data.append(weekday_totals.get(item["key"], 0))

    return {"labels": labels, "data": data}


def _build_status_chart(raw_rows: list[dict]) -> dict:
    config = read_json(settings.dashboard_config_path, {"status_labels": {}})
    labels = []
    data = []

    for row in raw_rows:
        labels.append(config["status_labels"].get(row["status"], row["status"]))
        data.append(row["total"])

    return {"labels": labels, "data": data}


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": settings.cors_allow_origins}})

    @app.get("/")
    def root():
        return jsonify(
            {
                "service": settings.dashboard_title,
                "framework": "Flask",
                "status": "running",
            }
        )

# статистика:
    @app.get("/api/dashboard")
    def dashboard():
        snapshot = repository.dashboard_snapshot()
        return jsonify(
            {
                "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
                "cards": [
                    {"label": "Пользователи", "value": snapshot["users_total"]},
                    {"label": "Брони", "value": snapshot["reservations_total"]},
                    {"label": "Активные столики", "value": snapshot["active_tables"]},
                    {"label": "Сообщения в поддержку", "value": support_messages_count()},
                ],
                "charts": {
                    "reservation_status": _build_status_chart(snapshot["reservation_statuses"]),
                    "weekday_load": _build_weekday_chart(snapshot["weekday_load"]),
                    "popular_tables": {
                        "labels": [
                            f"Столик {row['table_number']}" for row in snapshot["popular_tables"]
                        ],
                        "data": [row["total"] for row in snapshot["popular_tables"]],
                    },
                },
                "summary": {
                    "confirmed_reservations": snapshot["confirmed_total"],
                },
            }
        )

    return app


app = create_app()
