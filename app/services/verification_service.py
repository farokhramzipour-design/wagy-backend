import httpx
from fastapi import HTTPException

ZOHAL_API_URL_SHAHKAR = "https://dashboard.zohal.io/services/inquiry/shahkar"
ZOHAL_API_URL_POSTAL = "https://service.zohal.io/api/v0/services/inquiry/postal_code_inquiry"
ZOHAL_API_TOKEN = "2ba20e8b0699cb7e60937a198218049ccbc8dbe4"

async def verify_shahkar(mobile: str, national_code: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZOHAL_API_TOKEN}"
    }

    payload = {
        "mobile": mobile,
        "national_code": national_code
    }

    # Increase timeout to 30 seconds
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(ZOHAL_API_URL_SHAHKAR, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Verification failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error during verification: {str(e)}")

async def inquiry_postal_code(postal_code: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZOHAL_API_TOKEN}"
    }

    payload = {
        "postal_code": postal_code
    }

    # Increase timeout to 30 seconds
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(ZOHAL_API_URL_POSTAL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Postal code inquiry failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error during postal code inquiry: {str(e)}")
