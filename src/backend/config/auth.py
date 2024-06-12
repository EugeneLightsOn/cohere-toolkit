import os
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Add Auth strategy classes here to enable them
# Ex: [BasicAuthentication]
ENABLED_AUTH_STRATEGIES = []

# Define the mapping from Auth strategy name to class obj - does not need to be manually modified.
# During runtime, this will create an instance of each enabled strategy class.
# Ex: {"Basic": BasicAuthentication()}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls() for cls in ENABLED_AUTH_STRATEGIES}

# Token to authorize migration requests
MIGRATE_TOKEN = os.environ.get(
    "MIGRATE_TOKEN", None
)

security = HTTPBearer()


def verify_migrate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != MIGRATE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def is_authentication_enabled() -> bool:
    """
    Check whether any form of authentication was enabled.

    Returns:
        bool: Whether authentication is enabled.
    """
    if ENABLED_AUTH_STRATEGIES:
        return True

    return False
