from fastapi import APIRouter, Query, HTTPException, Header
from database import get_slave_connection, get_master_connection
from typing import Optional
import hashlib
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'scissors-bar-secret-key-2024')
ALLOWED_SORT_FIELDS = {"price", "name", "drama_level", "strength"}

@router.get("/menu")
def get_menu(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    drama_level: Optional[str] = None,
    min_strength: Optional[int] = Query(None, ge=0, le=100),
    max_strength: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("price"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    conn = None
    try:
        conn = get_slave_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM menu_items WHERE available = 1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if drama_level:
            query += " AND drama_level = %s"
            params.append(drama_level)
        
        if min_strength is not None:
            query += " AND strength >= %s"
            params.append(min_strength)
        
        if max_strength is not None:
            query += " AND strength <= %s"
            params.append(max_strength)
        
        if search:
            query += " AND name LIKE %s"
            params.append(f"%{search}%")
        
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "price"
        
        sort_direction = "ASC" if order.lower() == "asc" else "DESC"
        query += f" ORDER BY {sort_by} {sort_direction}"
        
        offset = (page - 1) * limit
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        return {
            "request": "menu",
            "data": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        return {
            "request": "menu",
            "data": [],
            "status": "fallback",
            "message": "Database unavailable"
        }
    finally:
        if conn:
            conn.close()

@router.get("/menu/secret")
def get_secret_menu(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {
            "request": "secret_menu",
            "result": [],
            "status": "unauthorized",
            "message": "Authorization required"
        }
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return {
            "request": "secret_menu",
            "result": [],
            "status": "invalid_token",
            "message": "Invalid or expired token"
        }
    
    conn = None
    try:
        conn = get_slave_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM secret_menu WHERE is_active = 1")
        items = cursor.fetchall()
        
        if items:
            return {
                "request": "secret_menu",
                "result": items,
                "count": len(items)
            }
        else:
            return {
                "request": "secret_menu",
                "result": [
                    {"id": 99, "name": "The Deer Penis", "price": 350.00, "category": "Шот", "drama_level": "gay_panic"},
                    {"id": 100, "name": "Scissors Cut", "price": 420.00, "category": "Коктейль", "drama_level": "high"}
                ],
                "status": "fallback"
            }
    except Exception as e:
        return {
            "request": "secret_menu",
            "result": [
                {"id": 99, "name": "The Deer Penis (FALLBACK)", "price": 350.00}
            ],
            "status": "fallback"
        }
    finally:
        if conn:
            conn.close()

@router.get("/auth/test-token")
def get_test_token():
    payload = {
        'user_id': 1,
        'username': 'test_user',
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"token": token}

@router.get("/api/hash/{str_input}")
def hash_string(str_input: str):
    result = hashlib.sha256(str_input.encode()).hexdigest()
    return {
        "request": str_input,
        "result": result
    }

@router.get("/analytics/drama-stats")
def get_drama_statistics():
    conn = None
    try:
        conn = get_slave_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                drama_level,
                COUNT(*) as drink_count,
                AVG(strength) as avg_strength,
                AVG(price) as avg_price
            FROM menu_items
            WHERE available = 1 AND drama_level IS NOT NULL
            GROUP BY drama_level
        """)
        stats = cursor.fetchall()
        
        return {
            "data": stats,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "data": [
                {"drama_level": "low", "drink_count": 4, "avg_strength": 12.5, "avg_price": 280.00},
                {"drama_level": "medium", "drink_count": 6, "avg_strength": 18.0, "avg_price": 350.00},
                {"drama_level": "high", "drink_count": 3, "avg_strength": 25.0, "avg_price": 420.00},
                {"drama_level": "gay_panic", "drink_count": 2, "avg_strength": 35.0, "avg_price": 500.00}
            ],
            "status": "fallback"
        }
    finally:
        if conn:
            conn.close()
