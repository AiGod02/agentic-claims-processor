import threading
from typing import Dict, Optional
from models.claim import ClaimResult


class ClaimsStore:
    def __init__(self):
        self._store: Dict[str, ClaimResult] = {}
        self._lock = threading.Lock()

    def save(self, result: ClaimResult) -> None:
        with self._lock:
            self._store[result.claim_id] = result

    def get(self, claim_id: str) -> Optional[ClaimResult]:
        with self._lock:
            return self._store.get(claim_id)

    def list_all(self) -> list:
        with self._lock:
            return list(self._store.values())


claims_store = ClaimsStore()
