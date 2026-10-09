"""Policy management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database.models import Policy
from models import PolicySchema
from typing import List

router = APIRouter()


@router.get("/api/policies", response_model=List[PolicySchema])
async def get_policies(db: Session = Depends(get_db)):
    """Get all security policies."""
    try:
        policies = db.query(Policy).all()
        return policies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/policies/{policy_id}", response_model=PolicySchema)
async def get_policy(policy_id: int, db: Session = Depends(get_db)):
    """Get a specific policy by ID."""
    try:
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return policy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/policies/{policy_id}", response_model=PolicySchema)
async def update_policy(policy_id: int, policy_update: PolicySchema, db: Session = Depends(get_db)):
    """Update a security policy."""
    try:
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Update fields
        if policy_update.description:
            policy.description = policy_update.description
        if policy_update.allowed_tools:
            policy.allowed_tools = policy_update.allowed_tools
        
        db.commit()
        db.refresh(policy)
        return policy
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
