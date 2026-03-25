from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.models.farmer import CompleteProfileRequest, UpdateFarmRequest
import logging

logger = logging.getLogger(__name__)


def _serialize_farmer(doc: dict) -> dict:
    """
    Converts MongoDB document to a JSON-serializable dict.
    Converts ObjectId → string, handles nested objects.
    """
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


class FarmerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.col = db.farmers   # shorthand

    async def get_by_phone(self, phone: str) -> dict | None:
        """Returns farmer document or None if not found."""
        doc = await self.col.find_one({"phone": phone})
        return _serialize_farmer(doc) if doc else None

    async def get_by_id(self, farmer_id: str) -> dict | None:
        """Returns farmer document by ID or None."""
        try:
            doc = await self.col.find_one({"_id": ObjectId(farmer_id)})
            return _serialize_farmer(doc) if doc else None
        except Exception:
            return None

    async def create_farmer(self, phone: str) -> dict:
        """
        Creates a minimal farmer record on first OTP verification.
        Profile is completed in a second step.
        """
        now = datetime.utcnow()
        doc = {
            "phone": phone,
            "name": None,
            "language": "english",
            "farm": None,
            "is_profile_complete": False,
            "created_at": now,
            "updated_at": now,
            "is_active": True,
        }
        result = await self.col.insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(f"New farmer created: {phone}, id: {result.inserted_id}")
        return _serialize_farmer(doc)

    async def complete_profile(
        self, phone: str, data: CompleteProfileRequest
    ) -> dict:
        """
        Sets name, language, and farm details after OTP verification.
        Called from the onboarding screen.
        """
        farmer = await self.get_by_phone(phone)
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found. Please verify OTP first."
            )

        update_data = {
            "name": data.name,
            "language": data.language,
            "is_profile_complete": True,
            "updated_at": datetime.utcnow(),
        }

        # Add farm details if provided
        if data.farm:
            farm_dict = data.farm.model_dump(exclude_none=True)
            # Convert planting_date if provided
            update_data["farm"] = farm_dict

        await self.col.update_one(
            {"phone": phone},
            {"$set": update_data}
        )

        updated = await self.get_by_phone(phone)
        logger.info(f"Profile completed for farmer: {phone}")
        return updated

    async def update_farm(self, farmer_id: str, data: UpdateFarmRequest) -> dict:
        """Updates farm details — called from settings screen."""
        update_data = {"updated_at": datetime.utcnow()}

        if data.name:
            update_data["name"] = data.name
        if data.language:
            update_data["language"] = data.language
        if data.farm:
            update_data["farm"] = data.farm.model_dump(exclude_none=True)

        result = await self.col.update_one(
            {"_id": ObjectId(farmer_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found."
            )

        return await self.get_by_id(farmer_id)

    async def deactivate(self, farmer_id: str) -> bool:
        """Soft delete — sets is_active=False."""
        result = await self.col.update_one(
            {"_id": ObjectId(farmer_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0