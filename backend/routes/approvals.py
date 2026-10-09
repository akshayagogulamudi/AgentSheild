"""Approval workflow routes for pending security decisions."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from database.models import PendingApproval, SecurityEvent
from models import PendingApprovalSchema
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter()


@router.get("/api/approvals", response_model=List[PendingApprovalSchema])
async def get_pending_approvals(
    db: Session = Depends(get_db),
    status: Optional[str] = Query("pending"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get pending approvals.
    
    Args:
        db: Database session
        status: Filter by status (pending, approved, rejected)
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of pending approvals
    """
    try:
        query = db.query(PendingApproval)
        
        if status:
            query = query.filter(PendingApproval.status == status)
        
        approvals = query.order_by(PendingApproval.timestamp.desc()).offset(offset).limit(limit).all()
        return approvals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/approvals/{approval_id}", response_model=PendingApprovalSchema)
async def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """
    Get a specific pending approval by ID.
    
    Args:
        approval_id: ID of pending approval
        db: Database session
        
    Returns:
        PendingApprovalSchema
    """
    try:
        approval = db.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        return approval
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/approvals/{approval_id}/approve")
async def approve_action(
    approval_id: int,
    approver_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Approve a pending action.
    
    Args:
        approval_id: ID of pending approval
        approver_email: Email of approver (optional)
        db: Database session
        
    Returns:
        Updated approval record
    """
    try:
        approval = db.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        if approval.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve action with status '{approval.status}'"
            )
        
        approval.status = "approved"
        approval.approved_at = datetime.utcnow()
        if approver_email:
            approval.approver_email = approver_email
        
        db.commit()
        db.refresh(approval)
        
        return {
            "id": approval.id,
            "status": approval.status,
            "approved_at": approval.approved_at,
            "message": f"Action approved by {approval.approver_email or 'system'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/approvals/{approval_id}/reject")
async def reject_action(
    approval_id: int,
    approver_email: Optional[str] = None,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Reject a pending action.
    
    Args:
        approval_id: ID of pending approval
        approver_email: Email of approver (optional)
        reason: Reason for rejection (optional)
        db: Database session
        
    Returns:
        Updated approval record
    """
    try:
        approval = db.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        if approval.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject action with status '{approval.status}'"
            )
        
        approval.status = "rejected"
        approval.approved_at = datetime.utcnow()
        if approver_email:
            approval.approver_email = approver_email
        if reason:
            approval.reason = reason
        
        db.commit()
        db.refresh(approval)
        
        return {
            "id": approval.id,
            "status": approval.status,
            "rejected_at": approval.approved_at,
            "message": f"Action rejected by {approval.approver_email or 'system'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/approvals/stats/summary")
async def get_approval_stats(db: Session = Depends(get_db)):
    """
    Get approval statistics.
    
    Args:
        db: Database session
        
    Returns:
        Summary statistics
    """
    try:
        pending_count = db.query(PendingApproval).filter(PendingApproval.status == "pending").count()
        approved_count = db.query(PendingApproval).filter(PendingApproval.status == "approved").count()
        rejected_count = db.query(PendingApproval).filter(PendingApproval.status == "rejected").count()
        
        return {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "total": pending_count + approved_count + rejected_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
