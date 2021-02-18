"""Machine learning routes/functions"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import get_db, Member, Family

router = APIRouter()


class PredResponse(BaseModel):
    """Internal validation to ensure pipeline returns correct dtypes.
    """
    member_id: int
    prediction: str
    details: str



@router.get("/predict-exit/{id}", response_model=PredResponse)
async def exit_prediction(id: int, session: Session=Depends(get_db)):
    """Takes member ID, gets 'member' and 'family' objects from DB, and calls
    prediction pipeline. Returns prediction object.
    """
    db_member = session.query(Member).filter(Member.id==id).first()
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    db_family = session.query(Family).filter(Family.id==db_member.family_id).first()

    return fake_predict(db_member, db_family)



def fake_predict(member, family):
    """A dummy prediction pipeline. Real pipeline should similarly take
    and wrangle the 'member' and 'family' objects from the request.
    """
    if family.vehicle['make'] == 'BMW':
        if member.barriers['alcohol_abuse']:
            prediction = 'Permanent'
        else:
            prediction = 'Unknown'
    else:
        prediction = 'Temporary'
    details = f'Explanation of {prediction}'[::-1]

    # Retain this return format. 'prediction' and 'details' must be strings.
    return {'member_id':member.id,
            'prediction':prediction,
            'details':details}