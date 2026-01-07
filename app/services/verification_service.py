import httpx
from fastapi import HTTPException

ZOHAL_API_URL_SHAHKAR = "https://service.zohal.io/api/v0/services/inquiry/shahkar"
ZOHAL_API_URL_POSTAL = "https://service.zohal.io/api/v0/services/inquiry/postal_code_inquiry"
ZOHAL_API_TOKEN = "9086cf483a563c995124a9bab75002763ec41eac"

async def verify_shahkar(mobile: str, national_code: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZOHAL_API_TOKEN}"
    }

    # Ensure mobile and national_code are strings and not None
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    if not national_code:
        raise HTTPException(status_code=400, detail="National code is required")

    payload = {
        "mobile": str(mobile),
        "national_code": str(national_code)
    }

    # Increase timeout to 30 seconds
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(ZOHAL_API_URL_SHAHKAR, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # If the API returns a 500 with a specific error message, we might want to parse it
            # But for now, just passing the detail is fine.
            # The specific error "invalid literal for int() with base 10: 'None'" suggests
            # the upstream API is failing to parse something, possibly because we sent None or a bad format.
            # By ensuring str() conversion above, we mitigate this on our end.
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
