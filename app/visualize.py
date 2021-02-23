"""Data visualization routes/functions"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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



@router.get("/moving-avg/{m}/{days_back}")
async def moving_avg(m: int, days_back: int, after_response: BackgroundTasks,
                session: Session=Depends(get_db)):
    """
    """
    _check_m(m)
    DoY = date.today().timetuple().tm_yday
    cache_path = os.path.join(PLOT_CACHE, f'MA{m}-{days_back}-d{DoY}.json')

    try:
        fig = json.load(open(cache_path))
    except FileNotFoundError:
        fig = json.loads(plot_moving_avg(session, m, days_back))
        after_response.add_task(_update_cache, 
            fig=fig, cache_path=cache_path, DoY=DoY)

    return fig


@router.get("/exit-pie/{m}")
async def exit_pie(m: int, after_response: BackgroundTasks,
                session: Session=Depends(get_db)):
    """
    """
    _check_m(m)
    DoY = date.today().timetuple().tm_yday
    cache_path = os.path.join(PLOT_CACHE, f'PIE{m}-d{DoY}.json')

    try:
        fig = json.load(open(cache_path))
    except FileNotFoundError:
        fig = json.loads(plot_exit_pie(session, m))
        after_response.add_task(_update_cache, 
            fig=fig, cache_path=cache_path, DoY=DoY)

    return fig




def plot_moving_avg(session, m, days_back):
    """
    """
    STEP = days_back//90 or 1
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m+days_back)
    big = _exit_df(session, first, last)

    moving = pd.DataFrame()
    for i in range(0, days_back, STEP):
        end = last - timedelta(days=i)
        start = end - timedelta(days=m)
        little = big[(big['date']>start) & (big['date']<=end)]
        breakdown = pd.DataFrame({dest:little[little['dest']==dest].shape[0]/little.shape[0] for dest in little['dest'].unique()}, index=[end])
        moving = moving.append(breakdown)
    moving = moving.fillna(0)

    fig = px.line(
        moving, 
        labels={'index':'date', 'value':'proportion'},
        title=f'{m}-Day Moving Averages',
        category_orders={'variable':
            ['Permanent Exit',
            'Temporary Exit',
            'Transitional Housing',
            'Emergency Shelter',
            'Unknown/Other']}
        )

    return json.dumps(fig, cls=PlotlyJSONEncoder)



def plot_exit_pie(session, m):
    """
    """
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m)
    df = _exit_df(session, first, last)
    df['count'] = 1

    fig = px.pie(
        df, values='count', names='dest'
        )

    return json.dumps(fig, cls=PlotlyJSONEncoder)




def _exit_df(session, first, last):
    """
    """
    exits = session.query(Member).filter((Member.date_of_exit>first) & (Member.date_of_exit<=last)).all()
    big = pd.DataFrame()
    for e in exits:
        big = big.append({
            'date':e.date_of_exit,
            'dest':e.exit_destination
        }, ignore_index=True)
    return big


def _update_cache(fig, cache_path, DoY):
    """
    """
    json.dump(fig, open(cache_path, 'w'))
    for file in os.scandir(PLOT_CACHE):
        if f'd{DoY}' not in file.name:
            os.remove(file.path)


def _check_m(m):
    """
    """
    if not (m == 90 or m == 365):
        raise HTTPException(status_code=404, detail="Not found. Try m=90 or m=365")