from pydantic import BaseModel, Field

# Pydantic модели для поддержки
class SupportMessageRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    message: str = Field(..., min_length=5, max_length=2000)
