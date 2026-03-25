import random
import string
import logging
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


def generate_otp(length: int = 6) -> str:
    """Generates a numeric OTP of given length."""
    return "".join(random.choices(string.digits, k=length))


async def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Sends OTP via Twilio SMS.
    Returns True on success, False on failure.
    Falls back to console log in development mode.
    """
    if settings.APP_ENV == "development" or not settings.TWILIO_ACCOUNT_SID:
        logger.info(f"[DEV MODE] OTP for {phone}: {otp}")
        print(f"\n{'='*40}")
        print(f"  DEV OTP for {phone}:  {otp}")
        print(f"{'='*40}\n")
        return True

    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your AgroAssist OTP is: {otp}. Valid for 10 minutes. Do not share.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        logger.info(f"OTP SMS sent to {phone}, SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP to {phone}: {e}")
        return False


async def store_otp(db, phone: str, otp: str):
    """
    Stores OTP in MongoDB otp_store collection.
    MongoDB TTL index auto-deletes it after 10 minutes.
    Upserts — replaces old OTP if farmer requests again.
    """
    await db.otp_store.update_one(
        {"phone": phone},
        {
            "$set": {
                "phone": phone,
                "otp": otp,
                "verified": False,
                "created_at": datetime.utcnow(),
                "attempts": 0,
            }
        },
        upsert=True,
    )


async def verify_otp(db, phone: str, otp: str) -> dict:
    """
    Verifies OTP from database.
    Returns dict with "success" bool and "reason" string.
    Limits to 5 attempts to prevent brute force.
    """
    record = await db.otp_store.find_one({"phone": phone})

    if not record:
        return {"success": False, "reason": "OTP not found or expired. Request a new one."}

    if record.get("verified"):
        return {"success": False, "reason": "OTP already used. Request a new one."}

    if record.get("attempts", 0) >= 5:
        return {"success": False, "reason": "Too many attempts. Request a new OTP."}

    # Increment attempt counter
    await db.otp_store.update_one(
        {"phone": phone},
        {"$inc": {"attempts": 1}}
    )

    if record["otp"] != otp:
        remaining = 4 - record.get("attempts", 0)
        return {"success": False, "reason": f"Incorrect OTP. {remaining} attempts left."}

    # Mark as verified — prevent reuse
    await db.otp_store.update_one(
        {"phone": phone},
        {"$set": {"verified": True}}
    )

    return {"success": True, "reason": "OTP verified successfully."}