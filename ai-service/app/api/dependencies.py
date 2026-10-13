from fastapi import Depends
from app.utils.security import verify_service_token

# Dependency to ensure requests originate from authenticated callers (or dev mode)
RequireServiceAuth = Depends(verify_service_token)
