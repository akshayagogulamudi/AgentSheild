"""File reading tool stub - simulated, non-functional."""
import json
from sqlalchemy.orm import Session
from database.models import SimulatedFile, ActivityLog


def read_file(filename: str, db: Session) -> dict:
    """
    Read a file from the simulated file collection.
    
    Args:
        filename: Name of file to read
        db: Database session
        
    Returns:
        Dictionary with file content or error
    """
    try:
        # Query the simulated file
        file_obj = db.query(SimulatedFile).filter(
            SimulatedFile.filename == filename
        ).first()
        
        if not file_obj:
            return {
                "success": False,
                "error": f"File not found: {filename}",
                "tool": "read_file"
            }
        
        # Record activity
        activity = ActivityLog(
            actor="tool_executor",
            action="read_file",
            details=json.dumps({
                "filename": filename,
                "classification": file_obj.classification.value,
                "success": True
            }),
            is_demo=False
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "filename": filename,
            "content": file_obj.content,
            "classification": file_obj.classification.value,
            "tool": "read_file"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": "read_file"
        }


def get_allowed_files(db: Session) -> list:
    """Get list of allowed files."""
    try:
        files = db.query(SimulatedFile).all()
        return [f.filename for f in files]
    except Exception:
        return []
