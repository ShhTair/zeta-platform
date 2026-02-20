from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.bot_config import BotConfig
from app.models.user import User
from app.schemas.bot_config import BotConfigCreate, BotConfigUpdate, BotConfigResponse
from app.dependencies.auth import get_current_user, require_city_admin
from app.middleware.audit import create_audit_log

router = APIRouter(tags=["Bot Configuration"])


@router.get("/cities/{city_id}/bot-config", response_model=BotConfigResponse)
def get_bot_config_public(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get bot configuration for a city (public endpoint for bots)"""
    config = db.query(BotConfig).filter(BotConfig.city_id == city_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    return config


@router.get("/cities/{city_id}/config", response_model=BotConfigResponse)
def get_bot_config(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bot configuration for a city (authenticated endpoint for admin)"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    config = db.query(BotConfig).filter(BotConfig.city_id == city_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    return config


@router.put("/cities/{city_id}/config", response_model=BotConfigResponse)
def update_bot_config(
    city_id: int,
    config_data: BotConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update or create bot configuration for a city"""
    # Check access
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    config = db.query(BotConfig).filter(BotConfig.city_id == city_id).first()
    
    if not config:
        # Create new config
        config = BotConfig(city_id=city_id, **config_data.model_dump(exclude_unset=True))
        db.add(config)
        db.commit()
        db.refresh(config)
        
        create_audit_log(
            db=db,
            user_id=current_user.id,
            city_id=city_id,
            action="CREATE",
            table_name="bot_configs",
            record_id=config.id,
            new_value=config_data.model_dump(exclude_unset=True)
        )
    else:
        # Update existing config
        old_values = {
            "system_prompt": config.system_prompt,
            "greeting_message": config.greeting_message,
            "manager_contact": config.manager_contact,
            "escalation_action": config.escalation_action.value if config.escalation_action else None
        }
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        db.commit()
        db.refresh(config)
        
        create_audit_log(
            db=db,
            user_id=current_user.id,
            city_id=city_id,
            action="UPDATE",
            table_name="bot_configs",
            record_id=config.id,
            old_value=old_values,
            new_value=update_data
        )
    
    return config
