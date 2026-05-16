from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.farmer import FarmDetails
import re


def normalize_phone(v: str) -> str:
    cleaned = v.strip()
    if not re.match(r"^\+?[1-9]\d{9,14}$", cleaned):
        raise ValueError("Invalid phone number. Use format: +919876543210")
    if not cleaned.startswith("+"):
        cleaned = "+91" + cleaned
    return cleaned


# Request schemas

class SendOTPRequest(BaseModel):
    phone: str = Field(..., example="+919876543210")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., example="+919876543210")
    otp: str = Field(..., min_length=6, max_length=6, example="482931")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class CompleteProfileRequest(BaseModel):
    """Called after OTP verification to complete farmer profile."""
    phone: str = Field(..., example="+919876543210")
    name: str = Field(..., min_length=2, max_length=100, example="Ramesh Patil")
    language: str = Field(default="english", example="marathi")
    farm: Optional[FarmDetails] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {"english", "marathi", "hindi", "kannada", "telugu"}
        v = v.lower().strip()
        if v not in allowed:
            raise ValueError(f"Language must be one of: {allowed}")
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateFarmRequest(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    farm: Optional[FarmDetails] = None


# Response schemas

class OTPSentResponse(BaseModel):
    message: str
    phone: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    farmer_id: str
    is_new_farmer: bool = Field(
        description="True on first login — frontend routes to profile setup"
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