from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GeoLocation(BaseModel):
    """GeoJSON Point for MongoDB 2dsphere index."""
    type: str = "Point"
    coordinates: list[float] = Field(
        ...,
        description="[longitude, latitude] in GeoJSON order",
        example=[74.1240, 16.7000]
    )


class FarmDetails(BaseModel):
    location: Optional[GeoLocation] = None
    area_acres: Optional[float] = Field(None, gt=0, example=5.5)
    crop_type: Optional[str] = Field(None, example="sugarcane")
    soil_type: Optional[str] = Field(None, example="black cotton")
    planting_date: Optional[datetime] = None


class FarmerDocument(BaseModel):
    """MongoDB document model for farmers collection."""
    phone: str
    name: Optional[str] = None
    language: str = "english"
    farm: Optional[FarmDetails] = None
    is_profile_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)