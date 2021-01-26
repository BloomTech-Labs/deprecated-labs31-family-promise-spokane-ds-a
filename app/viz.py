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

   fig = shap_predict(encoder.transform(X), model['classifier'])
   imdata = pickle.dumps(fig)
   jstr = json.dumps({"image": base64.b64encode(imdata).decode('ascii')})
   return jstr

def shap_predict(row, model, num_features=5):
      # TODO: Add db_manager to this so we can
      # easily get the df row. (might have to be inside of the main function.)
    pred = model.predict(row)[0]
    pred_index = np.where(model.classes_ == pred)[0][0]
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(row)

    #return shap_values
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
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
    fig.suptitle("Model's Predicted Endpoint: 'Permanent Housing'" , fontsize=16)
    y_pos = range(len(shap_summary['contributing_n_features']))
    features = shap_summary['contributing_n_features'][::-1].keys()
    values = shap_summary['contributing_n_features'][::-1].values
    maxes = []
    maxes.append(max(values))
    ax[0].barh(y_pos, values)
    ax[0].set_xlabel("Confidence")
    ax[0].set_yticks(y_pos)
    ax[0].set_yticklabels(features)
    ax[0].set_title("Features supporting Permanent Housing")
    y_pos = range(len(shap_summary['opposing_n_features']))
    features = shap_summary['opposing_n_features'].keys()
    values = abs(shap_summary['opposing_n_features'].values)
    maxes.append(max(values))
    ax[1].barh(y_pos, values, color='red')
    ax[1].set_xlabel("Confidence")
    ax[1].set_yticks(y_pos)
    ax[1].set_yticklabels(features)
    ax[1].set_title("Features opposing Permanent Housing")
    ax[0].set_xlim(0, max(maxes) + 1)
    ax[1].set_xlim(0, max(maxes) + 1)
    plt.tight_layout()

    return fig
