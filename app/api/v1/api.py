from fastapi import APIRouter
from app.api.v1.endpoints import auth, sitter, verification

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(sitter.router, prefix="/sitters", tags=["sitters"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
