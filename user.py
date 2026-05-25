from fastapi import APIRouter, HTTPException
import app.db.repository as repository
# публичные профили пользователей
router = APIRouter(prefix="/api/users", tags=["users"])

# просмотр профиля любого пользователя
@router.get("/{username}")
def get_user_profile(username: str):
    user = repository.get_user_by_name(username)
    if not user:
        raise HTTPException(404, f"Пользователь '{username}' не найден")

    return {
        "user_name": user["user_name"],
        "email": user.get("email"),
        "phone": user.get("phone"),
        "total_visits": user.get("total_visits", 0),
        "created_at": user.get("created_at"),
        "role": user.get("role", "customer")
    }