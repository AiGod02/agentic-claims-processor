from fastapi import APIRouter, HTTPException
from models.claim import ClaimSubmission, ClaimResult
from graph.orchestrator import process_claim
from services.claims_store import claims_store

router = APIRouter()


@router.post("/claims/submit", response_model=ClaimResult)
async def submit_claim(submission: ClaimSubmission):
    try:
        return await process_claim(submission)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/claims/{claim_id}", response_model=ClaimResult)
async def get_claim(claim_id: str):
    result = claims_store.get(claim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Claim not found")
    return result


@router.get("/claims/{claim_id}/trace")
async def get_trace(claim_id: str):
    result = claims_store.get(claim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {
        "claim_id": claim_id,
        "graph_path": result.graph_path,
        "trace": result.trace,
        "readable": result.trace.to_readable() if result.trace else ""
    }


@router.get("/claims")
async def list_claims():
    return claims_store.list_all()
