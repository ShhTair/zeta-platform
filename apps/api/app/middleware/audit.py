from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional
import json


def create_audit_log(
    db: Session,
    user_id: Optional[int],
    city_id: Optional[int],
    action: str,
    table_name: str,
    record_id: Optional[int] = None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None
):
    """Create an audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        city_id=city_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=json.dumps(old_value) if old_value else None,
        new_value=json.dumps(new_value) if new_value else None
    )
    db.add(audit_log)
    db.commit()
    return audit_log
