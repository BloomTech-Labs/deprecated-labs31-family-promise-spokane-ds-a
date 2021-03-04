"""Prediction routes/functions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db, Member, Family

import pandas as pd
import pickle

router = APIRouter()

PIPELINE = pickle.load(open('app/models/tree3.pickle', 'rb'))



### ROUTES ###

@router.get("/predict-exit/{id}")
async def exit_prediction(id: int, session: Session=Depends(get_db)):
    """Updates and returns exit prediction for given member ID.

    Path Parameters:
    - id (int) : Member ID.
    """
    member = session.query(Member).filter(Member.id==id).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    family = session.query(Family).filter(Family.id==member.family_id).first()

    member.predicted_exit_destination = exit_predict(member.__dict__, family.__dict__)
    session.commit()

    return {'member_id':member.id, 
            'exit_prediction':member.predicted_exit_destination}




### FUNCTIONS ###

def exit_predict(member, family):
    """A fully functional prediction pipeline, using a TERRIBLE model! 
    """
    norm = pd.concat([pd.json_normalize(member), pd.json_normalize(family)], axis=1)

    norm = _feat_engineer(norm)

    # Drop target, as well as '_sa_instance_state', which is part of the sqlalchemy
    # model object.
    norm = norm.drop(columns=['predicted_exit_destination', '_sa_instance_state'])

    # Drop KPI columns (for visualizations).
    norm = norm.drop(columns=['date_of_exit', 'income_at_exit', 'exit_destination'])

    return PIPELINE.predict(norm)[0]



def _feat_engineer(df):
    """This function should be identical to whatever feature engineering is going
    on in your model notebook.
    """
    df = df.copy()

    df['homeless_info.homeless_start_date'] = pd.to_datetime(df['homeless_info.homeless_start_date'])
    df['date_of_enrollment'] = pd.to_datetime(df['date_of_enrollment'])

    df['homeless_start_year'] = df['homeless_info.homeless_start_date'].dt.year
    df['homeless_start_doy'] = df['homeless_info.homeless_start_date'].dt.dayofyear

    df['year_of_enrollment'] = df['date_of_enrollment'].dt.year
    df['doy_of_enrollment'] = df['date_of_enrollment'].dt.dayofyear

    df = df.drop(columns=['homeless_info.homeless_start_date', 
                          'date_of_enrollment', 'id', 'family_id'])

    return df[sorted(df.columns)]