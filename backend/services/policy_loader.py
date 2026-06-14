import json
from functools import lru_cache
from config import settings


@lru_cache(maxsize=10)
def load_policy(policy_id: str) -> dict:
    """Load and cache policy from JSON. Returns raw dict (not Pydantic model)
    so agents can do flexible key access."""
    with open(settings.POLICY_FILE_PATH) as f:
        data = json.load(f)
    if data["policy_id"] != policy_id:
        raise ValueError(f"Policy {policy_id} not found in {settings.POLICY_FILE_PATH}")
    return data
