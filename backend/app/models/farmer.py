from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


# ub-models

class GeoLocation(BaseModel):
    """GeoJSON Point — used for MongoDB 2dsphere index."""
    type: str = "Point"
    coordinates: List[float] = Field(
        ...,
        description="[longitude, latitude] — GeoJSON order",
        example=[74.1240, 16.7000]
    )


class FarmDetails(BaseModel):
    location: Optional[GeoLocation] = None
    area_acres: Optional[float] = Field(None, gt=0, example=5.5)
    crop_type: Optional[str] = Field(None, example="grapes")
    soil_type: Optional[str] = Field(None, example="black cotton")
    planting_date: Optional[datetime] = None


# Request Schemas (what client sends)

class SendOTPRequest(BaseModel):
    phone: str = Field(..., example="+919876543210")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Accept formats: +919876543210 or 9876543210
        cleaned = v.strip()
        if not re.match(r"^\+?[1-9]\d{9,14}$", cleaned):
            raise ValueError("Invalid phone number. Use format: +919876543210")
        # Normalize to +91 format for India numbers
        if not cleaned.startswith("+"):
            cleaned = "+91" + cleaned
        return cleaned


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., example="+919876543210")
    otp: str = Field(..., min_length=6, max_length=6, example="482931")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned.startswith("+"):
            cleaned = "+91" + cleaned
        return cleaned


class CompleteProfileRequest(BaseModel):
    """
    Called after OTP verification to set up the farmer's profile.
    Phone must match the verified OTP session.
    """
    phone: str = Field(..., example="+919876543210")
    name: str = Field(..., min_length=2, max_length=100, example="Ramesh Patil")
    language: str = Field(default="english", example="marathi")
    farm: Optional[FarmDetails] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned.startswith("+"):
            cleaned = "+91" + cleaned
        return cleaned

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {"english", "marathi", "hindi", "kannada", "telugu"}
        v = v.lower().strip()
        if v not in allowed:
            raise ValueError(f"Language must be one of: {allowed}")
        return v


class LoginRequest(BaseModel):
    """
    Login = send OTP. This is a convenience wrapper.
    Farmers don't use passwords — only OTP.
    """
    phone: str = Field(..., example="+919876543210")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateFarmRequest(BaseModel):
    """Update farm details after initial setup."""
    name: Optional[str] = None
    language: Optional[str] = None
    farm: Optional[FarmDetails] = None


# Response Schemas (what server sends back)

class OTPSentResponse(BaseModel):
    message: str
    phone: str
    dev_otp: Optional[str] = Field(
        None,
        description="Only present in development mode — remove in production"
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    farmer_id: str
    is_new_farmer: bool = Field(
        description="True if this is first login — frontend should route to profile setup"
    )


class FarmerProfileResponse(BaseModel):
    id: str
    name: Optional[str]
    phone: str
    language: str
    farm: Optional[FarmDetails]
    created_at: datetime
    is_profile_complete: bool


class MessageResponse(BaseModel):
    message: str
    success: bool = True