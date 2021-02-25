"""Data visualization routes/functions"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from .db import get_db, Member

import os
import json
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

router = APIRouter()

PLOT_CACHE_DIR = 'app/plotcache'



@router.get("/exit-moving-avg/{m}/{days_back}")
async def moving_avg(m: int, days_back: int, after_response: BackgroundTasks,
                session: Session=Depends(get_db)):
    """Returns a lineplot (Plotly json) showing m-day moving averages of 
    the exit destination breakdown. Will only accept 90 or 365 as values for 
    m. The second parameter, days_back, determines the range of time on the 
    x-axis.
    """
    _check_m(m)
    DoY = date.today().timetuple().tm_yday
    cache_path = os.path.join(PLOT_CACHE_DIR, f'MA{m}-{days_back}-d{DoY}.json')

    try:
        with open(cache_path) as f:
            fig = json.load(f)
    except FileNotFoundError:
        fig = json.loads(plot_moving_avg(session, m, days_back))
        after_response.add_task(_update_cache, 
            fig=fig, cache_path=cache_path, DoY=DoY)

    return fig


@router.get("/exit-pie/{m}")
async def exit_pie(m: int, after_response: BackgroundTasks,
                session: Session=Depends(get_db)):
    """Returns a piechart (Plotly json) of the m-day exit breakdown. Will only 
    accept 90 or 365 as values for m.
    """
    _check_m(m)
    DoY = date.today().timetuple().tm_yday
    cache_path = os.path.join(PLOT_CACHE_DIR, f'PIE{m}-d{DoY}.json')

    try:
        with open(cache_path) as f:
            fig = json.load(f)
    except FileNotFoundError:
        fig = json.loads(plot_exit_pie(session, m))
        after_response.add_task(_update_cache, 
            fig=fig, cache_path=cache_path, DoY=DoY)

    return fig




def plot_moving_avg(session, m, days_back):
    """Query database, calculate exit breakdowns, and plot.
    """
    # 'STEP' makes sure Plotly isn't plotting at an obscene precision.
    STEP = days_back//90 or 1
    # 'last' should always be date.today(), but with no current data we need to go back
    # 180 days to see anything.
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m+days_back)
    df = _exit_df(session, first, last)
    dests = df['dest'].unique()

    # Calculate breakdown for all 'days_back' (at STEP precision).
    moving = pd.DataFrame()
    for i in range(0, days_back, STEP):
        end = last - timedelta(days=i)
        start = end - timedelta(days=m)
        sub = df[(df['date'] > start) & (df['date'] <= end)]
        n_exits = sub.shape[0]

        breakdown = {dest:sub[sub['dest']==dest].shape[0]/n_exits for dest in dests}
        moving = moving.append(pd.DataFrame(breakdown, index=[end]))
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

    return fig.to_json()



def plot_exit_pie(session, m):
    """Query database and pie.
    """
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m)
    df = _exit_df(session, first, last)
    df['count'] = 1

    fig = px.pie(
        df, values='count', color='dest', names='dest',
        color_discrete_map={
            'Permanent Exit':'#636EFA',
            'Temporary Exit':'#EF553B',
            'Transitional Housing':'#00CC96',
            'Emergency Shelter':'#AB63FA',
            'Unknown/Other':'#FFA15A'}
        )

    return fig.to_json()



def _exit_df(session, first, last):
    """Subfunction for querying database and returning only necessary stuff
    as a df.
    """
    exits = session.query(Member).filter((Member.date_of_exit > first)\
                & (Member.date_of_exit <= last)).all()
    df = pd.DataFrame()
    for e in exits:
        df = df.append({
            'date':e.date_of_exit,
            'dest':e.exit_destination
        }, ignore_index=True)
    return df


def _update_cache(fig, cache_path, DoY):
    """Saves new plot and then scans cache for any outdated plots, deleting them.
    """
    with open(cache_path, 'w') as f:
        json.dump(fig, f)
    for file in os.scandir(PLOT_CACHE_DIR):
        if f'd{DoY}' not in file.name:
            os.remove(file.path)


def _check_m(m):
    if not (m == 90 or m == 365):
        raise HTTPException(status_code=404, detail="Not found. Try m=90 or m=365")