"""Simple database GET endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.orm import Session
from . import db

router = APIRouter()


@router.get("/members/{id}")
async def read_member(id: int, session: Session=Depends(db.get_db)):
    db_member = db.get_member(session, id=id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member


@router.get("/families/{id}")
async def read_family(id: int, session: Session=Depends(db.get_db)):
    db_family = db.get_family(session, id=id)
    if db_family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return db_family
