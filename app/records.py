"""Simple GET endpoints for reading 'member' and 'family' records."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db, Member, Family

router = APIRouter()



@router.get("/member/{id}")
async def read_member(id: int, session: Session=Depends(get_db)):
    """Takes member ID and returns member object from DB.
    """
    db_member = session.query(Member).filter(Member.id==id).first()
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member



@router.get("/family/{id}")
async def read_family(id: int, session: Session=Depends(get_db)):
    """Takes family ID and returns family object from DB.
    """
    db_family = session.query(Family).filter(Family.id==id).first()
    if db_family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return db_family
