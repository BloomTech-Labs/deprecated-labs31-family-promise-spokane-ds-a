"""Machine learning routes/functions"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import get_db, Member, Family

import pandas as pd
import pickle

router = APIRouter()

PIPELINE = pickle.load(open('app/models/tree3.pickle', 'rb'))



class PredResponse(BaseModel):
    """Internal validation to ensure pipeline returns correct dtypes.
    """
    member_id: int
    exit_prediction: str



@router.get("/predict-exit/{id}", response_model=PredResponse)
async def exit_prediction(id: int, session: Session=Depends(get_db)):
    """Takes member ID and returns prediction. Also updates 'predicted_exit_destination'
    column in the database.
    """
    db_member = session.query(Member).filter(Member.id==id).first()
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    db_family = session.query(Family).filter(Family.id==db_member.family_id).first()

    db_member.predicted_exit_destination = exit_predict(db_member.__dict__, db_family.__dict__)
    session.commit()

    return {'member_id':db_member.id, 
            'exit_prediction':db_member.predicted_exit_destination}



def exit_predict(member, family):
    """A fully functional prediction pipeline, using a TERRIBLE model! 
    """
    norm = pd.concat([pd.json_normalize(member), pd.json_normalize(family)], axis=1)
    norm['date_of_enrollment'] = pd.to_datetime(norm['date_of_enrollment'])
    norm['homeless_info.homeless_start_date'] = pd.to_datetime(norm['homeless_info.homeless_start_date'])

    norm = _feat_engineer(norm)

    # Drop target, as well as '_sa_instance_state', which is part of the sqlalchemy
    # model object.
    norm = norm.drop(columns=['predicted_exit_destination', '_sa_instance_state'])

    return PIPELINE.predict(norm)[0]




def _feat_engineer(df):
    """This function should be identical to whatever feature engineering is going
    on in your model notebook.
    """
    df = df.copy()
    df['homeless_start_year'] = df['homeless_info.homeless_start_date'].dt.year
    df['homeless_start_doy'] = df['homeless_info.homeless_start_date'].dt.dayofyear

    df['year_of_enrollment'] = df['date_of_enrollment'].dt.year
    df['doy_of_enrollment'] = df['date_of_enrollment'].dt.dayofyear

    df = df.drop(columns=['homeless_info.homeless_start_date', 
                          'date_of_enrollment', 'id', 'family_id'])

    return df[sorted(df.columns)]