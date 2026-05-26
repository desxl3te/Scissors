from app.core.config import settings
from dashboard_service.app import app

# точка входа для запуска Flask дашборда
if __name__ == "__main__":
    app.run(
        host=settings.dashboard_host,
        port=settings.dashboard_port,
        debug=settings.debug,
    )
