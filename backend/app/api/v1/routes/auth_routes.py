import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongodb import get_db
from app.schemas.farmer_schema import (
    SendOTPRequest, VerifyOTPRequest, CompleteProfileRequest,
    RefreshTokenRequest, UpdateFarmRequest,
    OTPSentResponse, TokenResponse, FarmerProfileResponse, MessageResponse,
)
from app.services.farmer_service import FarmerService
from app.core.otp import generate_otp, send_otp_sms, store_otp, verify_otp
from app.core.auth import (
    create_access_token, create_refresh_token,
    decode_token, get_current_farmer,
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/send-otp",
    response_model=OTPSentResponse,
    summary="Send OTP to farmer's phone number",
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

    # Log OTP in development — never expose in response
    if settings.APP_ENV == "development":
        logger.debug(f"DEV OTP for {request.phone}: {otp}")

    return OTPSentResponse(
        message=f"OTP sent to {request.phone}",
        phone=request.phone,
    )


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="Verify OTP and receive JWT tokens",
)
async def verify_otp_route(request: VerifyOTPRequest, db=Depends(get_db)):
    result = await verify_otp(db, request.phone, request.otp)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["reason"],
        )

    service = FarmerService(db)
    farmer = await service.get_by_phone(request.phone)
    is_new = False

    if not farmer:
        farmer = await service.create_farmer(request.phone)
        is_new = True

    token_data = {"sub": farmer["id"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        farmer_id=farmer["id"],
        is_new_farmer=is_new,
    )


@router.post(
    "/complete-profile",
    response_model=FarmerProfileResponse,
    summary="Complete farmer profile after OTP verification",
)
async def complete_profile(
    request: CompleteProfileRequest,
    farmer=Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    updated = await service.complete_profile(request.phone, request)

    return FarmerProfileResponse(
        id=updated["id"],
        name=updated.get("name"),
        phone=updated["phone"],
        language=updated.get("language", "english"),
        farm=updated.get("farm"),
        created_at=updated["created_at"],
        is_profile_complete=updated.get("is_profile_complete", False),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Get new access token using refresh token",
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


@router.get(
    "/me",
    response_model=FarmerProfileResponse,
    summary="Get current farmer profile",
)
async def get_my_profile(
    farmer=Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    fetched = await service.get_by_id(str(farmer["_id"]))

    if not fetched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found.",
        )

    return FarmerProfileResponse(
        id=fetched["id"],
        name=fetched.get("name"),
        phone=fetched["phone"],
        language=fetched.get("language", "english"),
        farm=fetched.get("farm"),
        created_at=fetched["created_at"],
        is_profile_complete=fetched.get("is_profile_complete", False),
    )


@router.put(
    "/me/farm",
    response_model=FarmerProfileResponse,
    summary="Update farm details",
)
async def update_farm(
    request: UpdateFarmRequest,
    farmer=Depends(get_current_farmer),
    db=Depends(get_db),
):
    service = FarmerService(db)
    updated = await service.update_farm(str(farmer["_id"]), request)

    return FarmerProfileResponse(
        id=updated["id"],
        name=updated.get("name"),
        phone=updated["phone"],
        language=updated.get("language", "english"),
        farm=updated.get("farm"),
        created_at=updated["created_at"],
        is_profile_complete=updated.get("is_profile_complete", False),
    )