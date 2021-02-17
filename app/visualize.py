"""Data visualization routes/functions"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .db import get_db, Member

import json
from datetime import date, timedelta
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

router = APIRouter()



@router.get("/enrollments/{last_n_days}")
async def enrollment_count(last_n_days: int, session: Session=Depends(get_db)):
    """A template for our visualizations which will require selection of members 
    within a time range. Will not be able to do much with the current nearly empty 
    database.
    """
    cutoff_date = date.today() - timedelta(days=last_n_days)
    n_enrollments = session.query(Member).filter(Member.date_of_enrollment > cutoff_date).count()

    return n_enrollments



def plot(data):
    """Plotly template. JSON will be unpacked on the front end.
    """
    fig = px.bar(data)
    return json.dumps(fig, cls=PlotlyJSONEncoder)