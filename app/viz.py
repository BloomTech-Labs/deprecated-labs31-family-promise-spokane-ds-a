"""
   Data visualization functions

   This takes the top 3 features found in the model and auto
   generates 3 visuizations for the case manager to see.

   """

from fastapi import APIRouter
from app import ml, db_manager
from app.ml import predict, PersonInfo
from app.ml_2 import predicter
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
from joblib import load
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import shap
import matplotlib.pyplot as plt
import pickle
import base64
load_dotenv()

router = APIRouter()

@router.post('/Visualizations')
async def show_viz(guest_info: PersonInfo):
   # load the
   get_feats = predicter(guest_info)

   # Loading the pickled model
   #model = load('app/assets/randomforest_modelv3.pkl')

   # Extracting only the top 3 features from the model
   feats = get_feats['top_features']

   # The dictionary that will be returned containing all 3
   # Visualizations for the front end
   fig_list = {}

   # A for-loop to auto generate visualizations.
   for k, v in enumerate(feats):
      # Assigning the y variable to a listed version of v (the column in the dict)
      y = [v]

      # Making a numpy array to turn into a dataframe
      arr = np.array([feats[v]])
      df = pd.DataFrame(arr, columns=y)

      fig = px.bar(df)
      js = fig.to_json()
      fig_list[k] = js
      return fig_list

@router.post('/Shap_predict')
async def display_shap_predict(guest_info: PersonInfo):
   # load the
   get_feats = predicter(guest_info)

   # Loading the pickled model
   model = load('app/assets/randomforest_modelv3.pkl')

   results = db_manager.set_variables(guest_info.member_id)

   # Loads the pickled Model
   model = load('app/assets/randomforest_modelv3.pkl') #loads pickled model (using loblib)

   # Converts the dictionary to dataframe
   X = pd.DataFrame(results)

   # Renames the columns to the column names needed for the model.
   X.rename(columns={'case_members':'CaseMembers', 'race':'Race', 'ethnicity':'Ethnicity',
                     'current_age':'Current Age', 'gender':'Gender','length_of_stay':'Length of Stay',
                     'enrollment_length':'Days Enrolled in Project', 'household_type':'Household Type',
                     'barrier_count_entry':'Barrier Count at Entry'},inplace=True)

   encoder = model.named_steps['ord']
   encoded_columns = encoder.transform(X).columns

   #Gets figure
   fig = shap_predict(encoder.transform(X), model['classifier'])
   return fig.to_json()

def shap_predict(row, model, num_features=5):
    pred = model.predict(row)[0]

    pred_index = np.where(model.classes_ == pred)[0][0]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(row)

    feature_names = row.columns
    feature_values = row.values[0]

    shaps = pd.Series(shap_values[pred_index][0], zip(feature_names, feature_values))
    shaps = shaps.sort_values(ascending=False)

    #Shows the confidence levels of each prediction
    confidences = [abs(sum(i[0])) for i in shap_values]

    result = shaps.to_string()
    contributing_n_features = shaps[:num_features]
    opposing_n_features = shaps[-num_features:]

    shap_summary = {'model_prediction':pred[0],
                     'prediction_confidence_percent':confidences[pred_index]/sum(confidences),
                     'contributing_n_features':contributing_n_features,
                     'opposing_n_features':opposing_n_features}

    fig = make_subplots(
        rows=1, cols=2,
        horizontal_spacing = 0.4,
        column_titles=[],
        specs=[[{}, {}]],
        subplot_titles=("Features Supporting {}".format(pred[0]), "Features Opposing {}".format(pred[0])))

    y_pos = range(len(shap_summary['contributing_n_features']))
    features = shap_summary['contributing_n_features'][::-1].keys()
    features = [feature[0] + ': ' + str(feature[1]) for feature in features]
    values = shap_summary['contributing_n_features'][::-1].values

    maxes = []
    maxes.append(max(values))

    fig.add_trace(go.Bar(x=values, y=features, orientation='h', name="Supporting Features"), row=1, col=1)

    y_pos = range(len(shap_summary['opposing_n_features']))
    features = shap_summary['opposing_n_features'].keys()
    features = [feature[0] + ': ' + str(feature[1]) for feature in features]
    values = abs(shap_summary['opposing_n_features'].values)

    fig.add_trace(go.Bar(x=values, y=features, orientation='h', name="Opposing Features"), row=1, col=2)

    fig.update_xaxes(range=[0,max(maxes)], dtick=.2)
    fig.update_layout(title_text="Predicted Exit: {}".format(pred[0]), title_x=0.5)
    fig.update_layout(width=1400, height=500, template='plotly_white')
    return fig
