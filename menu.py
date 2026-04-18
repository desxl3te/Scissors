from fastapi import APIRouter, Query, HTTPException
from database import get_slave_connection, get_master_connection
from typing import Optional

router = APIRouter()

@router.get("/menu")
def get_menu(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    sort_by: str = Query("price", regex="^(price|name)$"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    
    conn = None
    try:
        conn = get_slave_connection()  # Чтение из Slave
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM menu_items WHERE available = 1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += f" ORDER BY {sort_by} {order}"
        
        # Пагинация на уровне SQL
        offset = (page - 1) * limit
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        return {
            "request": "menu",
            "result": items,
            "page": page,
            "limit": limit,
            "total": len(items)
        }
    except Exception as e:
        # Fallback ответ
        return {
            "request": "menu",
            "result": [],
            "status": "fallback",
            "message": "Database unavailable"
        }
    finally:
        if conn:
            conn.close()

@router.get("/menu/secret")
def get_secret_menu():
    
    conn = None
    try:
        conn = get_slave_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM secret_menu LIMIT 1")
        item = cursor.fetchone()
        
        if item:
            return {"request": "secret_menu", "result": [item]}
        else:
            return {"request": "secret_menu", "result": []}
    except Exception as e:
        # Fallback
        return {
            "request": "secret_menu",
            "result": [{"id": 99, "name": "The Deer Penis", "price": 350.00, "category": "Шот"}]
        }
    finally:
        if conn:
            conn.close()
