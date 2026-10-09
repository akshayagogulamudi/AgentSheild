"""Database search tool stub - simulated, non-functional."""
import json
from sqlalchemy.orm import Session
from database.models import SimulatedRecord, ActivityLog


def search_records(query: str, record_type: str = None, db: Session = None) -> dict:
    """
    Search simulated database records.
    
    Args:
        query: Search query string
        record_type: Optional record type filter (employee, customer, financial)
        db: Database session
        
    Returns:
        Dictionary with search results
    """
    if db is None:
        return {"success": False, "error": "Database session required"}
    
    try:
        # Build query
        q = db.query(SimulatedRecord)
        
        if record_type:
            q = q.filter(SimulatedRecord.record_type == record_type)
        
        # Simple string search in data field
        results = []
        for record in q.all():
            data = record.data
            if query.lower() in data.lower():
                results.append({
                    "id": record.id,
                    "type": record.record_type,
                    "data": json.loads(data),
                    "classification": record.classification.value
                })
        
        # Record activity
        activity = ActivityLog(
            actor="tool_executor",
            action="search_records",
            details=json.dumps({
                "query": query,
                "record_type": record_type,
                "results_count": len(results),
                "success": True
            }),
            is_demo=False
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "query": query,
            "record_type": record_type,
            "results": results,
            "count": len(results),
            "tool": "search_records"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": "search_records"
        }
