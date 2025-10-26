from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class HealthCheck(BaseModel):
    status: str = "OK"

class PredictionResult(BaseModel):
    has_mutation: bool
    disease: str
    confidence: float = Field(ge=0, le=1)
    message: str
    details: Optional[dict] = None

class AnalysisRequest(BaseModel):
    sequence: str = Field(..., description="The genetic sequence to analyze")
    patient_id: Optional[str] = None
    analysis_type: str = Field(
        default="comprehensive", 
        description="Type of analysis to perform",
        enum=["comprehensive", "sickle_cell", "breast_cancer"]
    )

class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
