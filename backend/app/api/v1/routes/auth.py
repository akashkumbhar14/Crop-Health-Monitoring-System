from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongodb import get_db
from app.models.farmer import (
    SendOTPRequest, VerifyOTPRequest, CompleteProfileRequest,
    RefreshTokenRequest, UpdateFarmRequest,
    OTPSentResponse, TokenResponse, FarmerProfileResponse, MessageResponse,
)
from app.services.farmer_service import FarmerService
from app.core.otp import generate_otp, send_otp_sms, store_otp, verify_otp
from app.core.auth import create_access_token, create_refresh_token, decode_token, get_current_farmer
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Send OTP

@router.post(
    "/send-otp",
    response_model=OTPSentResponse,
    summary="Send OTP to farmer's phone number",
    description="""
**registration/login.**

Sends a 6-digit OTP via SMS to the farmer's phone number.
- In **development mode**: OTP is printed to console (no real SMS sent).
- In **production**: OTP is sent via Twilio SMS.
- OTP expires automatically after **10 minutes**.
- Rate limited: max 3 OTPs per phone per hour (TODO: add Redis rate limiting).
    """,
)
async def send_otp(request: SendOTPRequest, db=Depends(get_db)):
    otp = generate_otp()
    await store_otp(db, request.phone, otp)

    sms_sent = await send_otp_sms(request.phone, otp)

    if not sms_sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send OTP. Please try again.",
        )

    response = OTPSentResponse(
        message=f"OTP sent to {request.phone}",
        phone=request.phone,
    )

    # In development, return OTP in response so you can test without SMS
    if settings.APP_ENV == "development":
        response.dev_otp = otp

    return response


# Verify OTP + Issue Tokens

@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="Verify OTP and receive JWT tokens",
    description="""
**registration/login.**

Verifies the 6-digit OTP. On success:
- Issues **access token** (valid 60 min) + **refresh token** (valid 30 days).
- If farmer is new → `is_new_farmer: true` → frontend routes to profile setup.
- If farmer exists → `is_new_farmer: false` → frontend routes to home screen.
- Max **5 incorrect attempts** before OTP is locked.
    """,
)
async def verify_otp_route(request: VerifyOTPRequest, db=Depends(get_db)):
    # 1. Verify OTP
    result = await verify_otp(db, request.phone, request.otp)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["reason"],
        )

    # 2. Get or create farmer
    service = FarmerService(db)
    farmer = await service.get_by_phone(request.phone)
    is_new = False

    if not farmer:
        farmer = await service.create_farmer(request.phone)
        is_new = True

    # 3. Issue JWT tokens
    token_data = {"sub": farmer["id"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        farmer_id=farmer["id"],
        is_new_farmer=is_new,
    )


# Complete Profile (new farmers only)
@router.post(
    "/complete-profile",
    response_model=FarmerProfileResponse,
    summary="Complete farmer profile after OTP verification",
    description="""
**only for new farmers.**

Called after verify-otp returns `is_new_farmer: true`.
Collects: name, preferred language, and farm GPS location.
After this, farmer is fully registered.
    """,
)
async def complete_profile(
    request: CompleteProfileRequest,
    farmer_id: str = Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    farmer = await service.complete_profile(request.phone, request)

    return FarmerProfileResponse(
        id=farmer["id"],
        name=farmer.get("name"),
        phone=farmer["phone"],
        language=farmer.get("language", "english"),
        farm=farmer.get("farm"),
        created_at=farmer["created_at"],
        is_profile_complete=farmer.get("is_profile_complete", False),
    )


# Refresh Token

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Get new access token using refresh token",
    description="""
Called when the access token expires.
Frontend sends the refresh token → gets a new access token.
No re-login required.
    """,
)
async def refresh_token(request: RefreshTokenRequest, db=Depends(get_db)):
    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Send a refresh token.",
        )

    farmer_id = payload.get("sub")
    service = FarmerService(db)
    farmer = await service.get_by_id(farmer_id)

    if not farmer or not farmer.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Farmer account not found or deactivated.",
        )

    token_data = {"sub": farmer_id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        farmer_id=farmer_id,
        is_new_farmer=False,
    )


# Get My Profile
@router.get(
    "/me",
    response_model=FarmerProfileResponse,
    summary="Get current farmer's profile",
    description="Returns the profile of the currently logged-in farmer. Requires Bearer token.",
)
async def get_my_profile(
    farmer_id: str = Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    farmer = await service.get_by_id(farmer_id)

    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found.",
        )

    return FarmerProfileResponse(
        id=farmer["id"],
        name=farmer.get("name"),
        phone=farmer["phone"],
        language=farmer.get("language", "english"),
        farm=farmer.get("farm"),
        created_at=farmer["created_at"],
        is_profile_complete=farmer.get("is_profile_complete", False),
    )


# Update Farm Details

@router.put(
    "/me/farm",
    response_model=FarmerProfileResponse,
    summary="Update farm details",
    description="Update farm location, crop type, area etc. Requires Bearer token.",
)
async def update_farm(
    request: UpdateFarmRequest,
    farmer_id: str = Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    farmer = await service.update_farm(farmer_id, request)

    return FarmerProfileResponse(
        id=farmer["id"],
        name=farmer.get("name"),
        phone=farmer["phone"],
        language=farmer.get("language", "english"),
        farm=farmer.get("farm"),
        created_at=farmer["created_at"],
        is_profile_complete=farmer.get("is_profile_complete", False),
    )