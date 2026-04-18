from fastapi import FastAPI

app = FastAPI(title="Bar Core Service")

@app.get("/")
def root():
    return {"service": "Core", "framework": "FastAPI", "status": "running"}

@app.get("/api/menu")
def get_menu():
    return {
        "request": "menu",
        "result": [
            {"id": 1, "name": "Пиво", "price": 300},
            {"id": 2, "name": "Коктейль", "price": 450}
        ]
    }

@app.get("/api/menu/secret")
def get_secret_menu():
    return {
        "request": "secret_menu",
        "result": [{"id": 99, "name": "Олений пенис", "price": 500, "volume_ml": 50}]
    }