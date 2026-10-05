from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.automation import (
    AutomationRuleResponse, AutomationRuleCreate, AutomationRuleUpdate,
    AutomationEventResponse
)
from app.services.automation_service import automation_service
from app.api.deps import get_current_admin
from app.models.user import User

router = APIRouter(tags=["Automation"])

@router.get("/halls/{id}/automation/rules", response_model=List[AutomationRuleResponse])
async def get_hall_automation_rules(id: str, db: AsyncSession = Depends(get_db)):
    rules = await automation_service.get_rules(db, id)
    return [AutomationRuleResponse.model_validate(r) for r in rules]

@router.post("/halls/{id}/automation/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    id: str,
    rule_in: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    rule_in.hall_id = id
    rule = await automation_service.create_rule(db, rule_in)
    return AutomationRuleResponse.model_validate(rule)

@router.put("/automation/rules/{id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    id: str,
    rule_in: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    rule = await automation_service.update_rule(db, id, rule_in)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return AutomationRuleResponse.model_validate(rule)

@router.get("/halls/{id}/automation/events", response_model=List[AutomationEventResponse])
async def get_hall_automation_events(id: str, db: AsyncSession = Depends(get_db)):
    events = await automation_service.get_events(db, id)
    return [AutomationEventResponse.model_validate(e) for e in events]
