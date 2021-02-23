"""Data visualization routes/functions"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .db import get_db, Member

import os
import json
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

router = APIRouter()

PLOT_CACHE = 'app/plotcache'


@router.get("/moving-avg-90/{days_back}")
async def moving_avg_90(days_back: int, session: Session=Depends(get_db)):
    """
    """
    M = 90
    DoY = date.today().timetuple().tm_yday
    cache_path = os.path.join(PLOT_CACHE, f'MA90-{DoY}.json')

    try:
        fig = json.load(open(cache_path))
    except FileNotFoundError:
        for file in os.scandir(PLOT_CACHE):
            if 'MA90' in file.name:
                os.remove(file.path)
        fig = json.loads(_plot(session, M, days_back))
        json.dump(fig, open(cache_path, 'w'))

    return fig



def _plot(session, M, days_back):
    """
    """
    STEP = days_back//90 or 1
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=M+days_back)
    exits = session.query(Member).filter((Member.date_of_exit>first) & (Member.date_of_exit<=last)).all()
    big = pd.DataFrame()
    for e in exits:
        big = big.append({
            'date':e.date_of_exit,
            'dest':e.exit_destination,
        }, ignore_index=True)

    moving = pd.DataFrame()
    for i in range(0, days_back, STEP):
        end = last - timedelta(days=i)
        start = end - timedelta(days=M)
        little = big[(big['date']>start) & (big['date']<=end)]
        breakdown = pd.DataFrame({dest:little[little['dest']==dest].shape[0]/little.shape[0] for dest in little['dest'].unique()}, index=[end])
        moving = moving.append(breakdown)
    moving = moving.fillna(0)

    fig = px.line(
        moving, 
        labels={'index':'date', 'value':'proportion'},
        title=f'{M}-Day Moving Averages',
        category_orders={'variable':
            ['Permanent Exit',
            'Temporary Exit',
            'Transitional Housing',
            'Emergency Shelter',
            'Unknown/Other']}
        )

    return json.dumps(fig, cls=PlotlyJSONEncoder)