from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services import verification_service
from app.core.security import get_current_user_token
from app.core.config import settings
from jose import jwt
from uuid import UUID
from typing import Optional

router = APIRouter()

class ShahkarVerificationRequest(BaseModel):
    mobile: str
    national_code: str

class ShahkarVerificationResponse(BaseModel):
    success: bool
    data: dict = {}
    message: str = ""

class PostalCodeInquiryRequest(BaseModel):
    postal_code: str

class PostalCodeAddress(BaseModel):
    building_name: Optional[str]
    description: Optional[str]
    district: Optional[str]
    floor: Optional[str]
    number: Optional[int]
    province: Optional[str]
    side_floor: Optional[str]
    street: Optional[str]
    street2: Optional[str]
    town: Optional[str]

class PostalCodeInquiryResponse(BaseModel):
    success: bool
    address: Optional[PostalCodeAddress] = None
    raw_data: dict = {}
    message: str = ""

def get_current_user_id(token: str = Depends(get_current_user_token)) -> UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/shahkar", response_model=ShahkarVerificationResponse)
async def verify_shahkar_identity(
    request: ShahkarVerificationRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    try:
        result = await verification_service.verify_shahkar(request.mobile, request.national_code)
        return ShahkarVerificationResponse(success=True, data=result, message="Verification request processed")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/postal-code", response_model=PostalCodeInquiryResponse)
async def inquiry_postal_code(
    request: PostalCodeInquiryRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    try:
        result = await verification_service.inquiry_postal_code(request.postal_code)
        
        # Parse the response to extract address
        address_data = None
        if result.get("result") == 1 and result.get("response_body", {}).get("data", {}).get("address"):
            raw_address = result["response_body"]["data"]["address"]
            address_data = PostalCodeAddress(**raw_address)
            
        return PostalCodeInquiryResponse(
            success=True, 
            address=address_data, 
            raw_data=result, 
            message="Postal code inquiry processed"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
