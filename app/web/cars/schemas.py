from pydantic import BaseModel, Field, validator
from typing import Optional

class CarBase(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    category: Optional[str] = None


class CarCreate(BaseModel):
    make: str
    model: str
    year: int = Field(..., ge=1900, le=2100)
    category: str 


class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2100)
    category: Optional[str] = None


class CarOut(BaseModel):
    id: int
    make_id: int
    model_id: int
    year: int
    category: str

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str

    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query must be a non-empty string')
        return v.strip()
    
class QueryResponse(BaseModel):
    response: str
