import os
from typing import Optional

def verify_bearer_token(token: Optional[str]) -> bool:
    """Verify the bearer token for authentication"""
    expected_token = os.getenv("BEARER_TOKEN", "astroguide2024")
    return token == expected_token

def get_my_number() -> str:
    """Get the phone number in required format"""
    return os.getenv("MY_NUMBER", "918920560661")
