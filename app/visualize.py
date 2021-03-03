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
ALLOWED_FEATS = ['DEST', 'INC', 'LEN']
ALLOWED_M = [90, 365]


### ROUTES ###

@router.get("/moving-avg-{feature}/{m}-{days_back}")
async def moving_avg(
    feature: str,           # 'DEST', 'INC', or 'LEN'
    m: int,                 # 90 or 365
    days_back: int,
    after: BackgroundTasks,
    session: Session=Depends(get_db)):
    """Returns a lineplot (Plotly JSON) showing m-day moving averages of the given feature.

    Path Parameters:
    - feature (str) : Feature to plot. Accepts 'DEST' (exit destination), 'INC' (income change), or 'LEN' (length of stay).
    - m (int) : Number of days considered in each moving average calculation. Only accepts 90 or 365.
    - days_back (int) : Date range to plot, in days prior to the present day.
    """
    _check_valid(feature, m)
    plot_id = f'{feature}-MA'
    return get_plot(plot_id, session, after, {'m':m, 'days_back':days_back})
    

@router.get("/pie-{feature}/{m}")
async def moving_avg(
    feature: str,           # 'DEST', 'INC', or 'LEN'
    m: int,                 # 90 or 365
    after: BackgroundTasks,
    session: Session=Depends(get_db)):
    """Returns a piechart (Plotly JSON) of the given feature.

    Path Parameters:
    - feature (str) : Feature to plot. Accepts 'DEST' (exit destination), 'INC' (income change), or 'LEN' (length of stay).
    - m (int) : Number of days considered in the calculation. Only accepts 90 or 365.
    """
    _check_valid(feature, m)
    plot_id = f'{feature}-PIE'
    return get_plot(plot_id, session, after, {'m':m})




### TOP-LEVEL FUNCTIONS/CLASSES ###

def get_plot(plot_id, session, after, params):
    """Returns plot as a dict, either from cache or from new calculation. Updates cache after response.
    """
    cache_name = f'{plot_id}-{"-".join([str(params[p]) for p in params])}-d{_DoY()}.json'
    cache_path = os.path.join(PLOT_CACHE_DIR, cache_name)
    try:
        with open(cache_path) as f:
            plot = json.load(f)
    except FileNotFoundError:
        plot_func = PLOT_FUNCS[plot_id]
        plot = json.loads(plot_func(session, **params))
        after.add_task(_update_cache, plot=plot, cache_path=cache_path)
    return plot


class Plotter:
    """This class is the centerpiece of the visualization functionality. It is initialized
    given:
    - a feature (must be one of the features returned by '_exit_df()'
    - a list of categories for that feature (must actually be correspond to the values in the column)
    - a colormap from 'plotly.express.colors.qualitative'. 
    
    Holding these parameters in a class instance makes it much easier to ensure category colors
    are consistent across API calls, and limits other unnecessary parameter passing.
    """
    def __init__(self, feature, categories, cmap):
        self.feature = feature
        self.categories = categories
        self.discrete_cmap = {cat:color for cat, color in zip(categories, cmap)}

    def plot_moving(self, session, m, days_back):
        """Returns lineplot of the moving average.
        """
        first, last = _date_range(m, days_back)
        df = _exit_df(session, first, last)
        # 'STEP' makes sure Plotly isn't plotting at an obscene precision.
        STEP = days_back//90 or 1
        # Calculate breakdown for all 'days_back' (at STEP precision).
        moving = pd.DataFrame()
        for i in range(0, days_back, STEP):
            end = last - timedelta(days=i)
            start = end - timedelta(days=m)
            sub = df[(df['Date'] > start) & (df['Date'] <= end)]
            n_exits = sub.shape[0]

            # 'breakdown' is the proportion of each category out of the total exits for
            # this subset ('n_exits').
            breakdown = {cat:sub[sub[self.feature]==cat].shape[0]/n_exits for cat in self.categories}
            moving = moving.append(pd.DataFrame(breakdown, index=[end]))
        moving = moving.fillna(0)

        fig = px.line(
            moving, 
            labels={'index':'Date', 'value':'Proportion', 'variable':'Category'},
            color_discrete_map=self.discrete_cmap
        )
        return fig.to_json()

    def plot_pie(self, session, m):
        """Returns piechart.
        """
        first, last = _date_range(m)
        df = _exit_df(session, first, last)
        # 'px.pie()' needs each entry to have some numerical value, hence this 'count' column.
        df['count'] = 1

        fig = px.pie(
            df, values='count', color=self.feature, names=self.feature,
            color_discrete_map=self.discrete_cmap
        )
        return fig.to_json()


# Predefined Plotter objects.
dest_plots = Plotter(
    feature='Destination',
    categories=['Permanent Exit', 'Temporary Exit', 
                'Transitional Housing', 'Emergency Shelter', 
                'Unknown/Other'],
    cmap=cmaps.Safe
)
inc_plots = Plotter(
    feature='Income Category',
    categories=['Increased', 'Decreased', 'No Change', 'NO DATA'],
    cmap=cmaps.T10
)
len_plots = Plotter(
    feature='Length Of Stay',
    categories=["<2 weeks", "2-9 weeks", ">2 months"],
    cmap=cmaps.Dark2
)


# Dict so 'get_plot()' can select the correct Plotter method.
PLOT_FUNCS = {
    'DEST-MA':dest_plots.plot_moving,
    'DEST-PIE':dest_plots.plot_pie,
    'INC-MA':inc_plots.plot_moving,
    'INC-PIE':inc_plots.plot_pie,
    'LEN-MA':len_plots.plot_moving,
    'LEN-PIE':len_plots.plot_pie
}




### LOWER-LEVEL FUNCTIONS FOR 'Plotter' ###

def _date_range(m, days_back=0):
    """Returns two datetime objects to query between.
    """
    # 'last' should always be date.today(), but with no current data we need to go back
    # 180 days to see anything.
    last = date.today() - timedelta(days=180)
    first = last - timedelta(days=m+days_back)
    return first, last


def _exit_df(session, first, last):
    """Queries database for all members who exited in given date range, returning a DataFrame.
    """
    exits = session.query(Member).filter((Member.date_of_exit > first)\
                & (Member.date_of_exit <= last)).all()
    df = pd.DataFrame()
    for ex in exits:
        df = df.append({
            'Date':ex.date_of_exit,
            'Destination':ex.exit_destination,
            'Income Category':_inc_categories(ex.demographics['income'], ex.income_at_exit),
            'Length Of Stay':_len_categories(ex.date_of_enrollment, ex.date_of_exit)
        }, ignore_index=True)
    return df


def _inc_categories(inc_entry, inc_exit):
    """Returns an income category for given income-at-entry and income-at-exit.
    """
    if inc_exit > inc_entry:
        return 'Increased'
    elif inc_exit < inc_entry and inc_exit != -1:
        return 'Decreased'
    elif inc_exit == inc_entry == -1:
        return 'NO DATA'
    else:
        return 'No Change'


def _len_categories(date_enrollment, date_exit):
    """Returns a length category for given date-of-enrollment and date-of-exit.
    """
    delta = (date_exit - date_enrollment).days
    if delta < 14:
        return "<2 weeks"
    elif delta >= 14 and delta < 62:
        return "2-9 weeks"
    elif delta >= 62:
        return ">2 months"



### LOWER-LEVEL FUNCTIONS FOR ROUTES AND 'get_plot()' ###

def _check_valid(feature, m):
    """Ensures valid values for path parameters.
    """
    if feature not in ALLOWED_FEATS:
        raise HTTPException(status_code=404, detail=f"Feature '{feature}' not found.")
    if m not in ALLOWED_M:
        raise HTTPException(status_code=404, detail=f"Not found. '{m}' is an invalid value for m.")


def _DoY():
    """Returns current day of year.
    """
    return date.today().timetuple().tm_yday


def _update_cache(plot, cache_path):
    """Saves new plot and then scans cache for any outdated plots, deleting them.
    """
    with open(cache_path, 'w') as f:
        json.dump(plot, f)
    # Delete any files created on a day besides today.
    for file in os.scandir(PLOT_CACHE_DIR):
        if f'd{_DoY()}' not in file.name:
            os.remove(file.path)