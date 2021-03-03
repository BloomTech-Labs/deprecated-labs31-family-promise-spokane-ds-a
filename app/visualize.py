"""Data visualization routes/functions."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .db import get_db, Member

import os
import json
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
from plotly.express.colors import qualitative as cmaps 

router = APIRouter()

PLOT_CACHE_DIR = 'app/plotcache'

DEST_CATS = ['Permanent Exit', 'Temporary Exit', 
            'Transitional Housing', 'Emergency Shelter', 
            'Unknown/Other']
INC_CATS = ['Increased', 'Decreased', 'No Change', 'NO DATA']



### ROUTES ###

@router.get("/moving-avg-{feature}/{m}-{days_back}")
async def moving_avg(
    feature: str,           # 'DEST' or 'INC'
    m: int,                 # 90 or 365
    days_back: int,
    after: BackgroundTasks,
    session: Session=Depends(get_db)):
    """Returns a lineplot (Plotly JSON) showing m-day moving averages of the given feature.

    Path Parameters:
    - feature (str) : Feature to plot. Only accepts 'DEST' (exit destination) or 'INC' (income change).
    - m (int) : Number of days considered in each moving average calculation. Only accepts 90 or 365.
    - days_back (int) : Date range to plot, in days prior to the present day.
    """
    _check_valid(feature, m)
    plot_id = f'MA-{feature}'
    return vis(plot_id, session, after, {'m':m, 'days_back':days_back})
    

@router.get("/pie-{feature}/{m}")
async def moving_avg(
    feature: str,           # 'DEST' or 'INC'
    m: int,                 # 90 or 365
    after: BackgroundTasks,
    session: Session=Depends(get_db)):
    """Returns a piechart (Plotly JSON) of the given feature.

    Path Parameters:
    - feature (str) : Feature to plot. Only accepts 'DEST' (exit destination) or 'INC' (income change).
    - m (int) : Number of days considered in each moving average calculation. Only accepts 90 or 365.
    """
    _check_valid(feature, m)
    plot_id = f'PIE-{feature}'
    return vis(plot_id, session, after, {'m':m})




### TOP-LEVEL FUNCTIONS ###

def vis(plot_id, session, after, params):
    """
    """
    cache_name = f'{plot_id}-{"-".join([str(params[p]) for p in params])}-d{_DoY()}.json'
    cache_path = os.path.join(PLOT_CACHE_DIR, cache_name)

    try:
        with open(cache_path) as f:
            fig = json.load(f)
    except FileNotFoundError:
        plot_func = PLOT_FUNCS[plot_id]
        fig = json.loads(plot_func(session, **params))
        after.add_task(_update_cache, fig=fig, cache_path=cache_path)

    return fig


def plot_dest_moving_avg(session, m, days_back):
    """Queries database, calculates destination breakdowns, and returns plot.
    """
    first, last = _date_range(m, days_back)
    df = _exit_df(session, first, last)

    return _plot_moving(
        df, 'dest',
        DEST_CATS,
        last, m, days_back,
        cmaps.Safe
    )


def plot_inc_moving_avg(session, m, days_back):
    """Queries database, calculates income breakdowns, and returns plot.
    """
    first, last = _date_range(m, days_back)
    df = _exit_df(session, first, last)
    df['inc_cat'] = df.apply(_income_categories, axis=1)

    return _plot_moving(
        df, 'inc_cat',
        INC_CATS,
        last, m, days_back,
        cmaps.T10
    )


def plot_dest_pie(session, m):
    """Queries database, calculates destination breakdown, and returns plot.
    """
    first, last = _date_range(m)
    df = _exit_df(session, first, last)

    return _plot_pie(
        df, 'dest',
        DEST_CATS,
        cmaps.Safe
    )


def plot_inc_pie(session, m):
    """Queries database, calculates income breakdown, and returns plot.
    """
    first, last = _date_range(m)
    df = _exit_df(session, first, last)
    df['inc_cat'] = df.apply(_income_categories, axis=1)

    return _plot_pie(
        df, 'inc_cat',
        INC_CATS,
        cmaps.T10
    )


PLOT_FUNCS = {
    'MA-DEST':plot_dest_moving_avg,
    'MA-INC':plot_inc_moving_avg,
    'PIE-DEST':plot_dest_pie,
    'PIE-INC':plot_inc_pie
}



### LOWER FUNCTIONS ###

def _plot_moving(df, cat_column, categories, last, m, days_back, cmap):
    """
    """
    # 'STEP' makes sure Plotly isn't plotting at an obscene precision.
    STEP = days_back//90 or 1
    # Calculate breakdown for all 'days_back' (at STEP precision).
    moving = pd.DataFrame()
    for i in range(0, days_back, STEP):
        end = last - timedelta(days=i)
        start = end - timedelta(days=m)
        sub = df[(df['date'] > start) & (df['date'] <= end)]
        n_exits = sub.shape[0]

        # 'breakdown' is the proportion of each category out of the total exits for
        # this subset ('n_exits').
        breakdown = {cat:sub[sub[cat_column]==cat].shape[0]/n_exits for cat in categories}
        moving = moving.append(pd.DataFrame(breakdown, index=[end]))
    moving = moving.fillna(0)

    fig = px.line(
        moving, 
        labels={'index':'date', 'value':'proportion'},
        color_discrete_map={cat:color for cat, color in zip(categories, cmap)}
        )
    return fig.to_json()


def _plot_pie(df, cat_column, categories, cmap):
    """
    """
    # 'px.pie()' needs each entry to have some numerical value, hence this 'count' column.
    df['count'] = 1

    fig = px.pie(
        df, values='count', color=cat_column, names=cat_column,
        color_discrete_map={cat:color for cat, color in zip(categories, cmap)}
    )
    return fig.to_json()


def _income_categories(row):
    if row['inc_exit'] > row['inc_entry']:
        return 'Increased'
    elif row['inc_exit'] < row['inc_entry'] and row['inc_exit'] != -1:
        return 'Decreased'
    elif row['inc_exit'] == row['inc_entry'] == -1:
        return 'NO DATA'
    else:
        return 'No Change'


def _date_range(m, days_back=0):
    # 'last' should always be date.today(), but with no current data we need to go back
    # 180 days to see anything.
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m+days_back)
    return first, last


def _exit_df(session, first, last):
    """Queries database for all members who exited in given date range, returning date and destination data as a DataFrame.
    """
    exits = session.query(Member).filter((Member.date_of_exit > first)\
                & (Member.date_of_exit <= last)).all()
    df = pd.DataFrame()
    for ex in exits:
        df = df.append({
            'date':ex.date_of_exit,
            'dest':ex.exit_destination,
            'inc_entry':ex.demographics['income'],
            'inc_exit':ex.income_at_exit
        }, ignore_index=True)
    return df



def _update_cache(fig, cache_path):
    """Saves new plot and then scans cache for any outdated plots, deleting them.
    """
    with open(cache_path, 'w') as f:
        json.dump(fig, f)
    # Delete any files created on a day besides today.
    for file in os.scandir(PLOT_CACHE_DIR):
        if f'd{_DoY()}' not in file.name:
            os.remove(file.path)


def _DoY():
    """Returns current day of year.
    """
    return date.today().timetuple().tm_yday


def _check_valid(feature, m):
    """Ensures valid values for path parameters.
    """
    if not (m == 90 or m == 365):
        raise HTTPException(status_code=404, detail="Not found. Try m = 90 or 365")
    if not (feature == 'DEST' or feature == 'INC'):
        raise HTTPException(status_code=404, detail="Not found. Try feature = 'DEST' or 'INC'")