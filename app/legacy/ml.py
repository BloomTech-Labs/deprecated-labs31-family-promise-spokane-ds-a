"""Machine learning functions This file gets the data from the db_manager module 
   and perform the prediction with th emodel """
import random
import logging
from fastapi import APIRouter
from pydantic import BaseModel,Field,validator
import datetime
from joblib import load
import pandas as pd
from app import db_manager

router = APIRouter()
class PersonInfo(BaseModel):
    '''Data model for Request Body 
       
    personal_id: Personal_id (int) Sample 14245
    Data Subject to change once a working model is done'''
    # Features
    # features = [ 'CaseMembers','Race, 'Ethnicity', 'Current Age', 
    #              'Gender', 'Length of Stay', 'Enrollment Length',
    #              'Household Type', 'Barrier Count at Entry']  
    member_id: int = Field(...,example=2) #Gets member id from web team 

    def to_df(self):
        """Convert pydantic object to pandas dataframe with 1 row."""
        return pd.DataFrame([dict(self)])
    
    @validator('member_id')
    def variable_validation(cls,value):
        '''Validate member id is 0 or greater than 0 '''
        assert value >= 0, f'member_id == {value} must be > 0'
        return value

@router.post('/predict')
async def predict(guest_info: PersonInfo):
    '''# Data model base working model 
       # Usage: 
         - member_id (integer) Exmple : 232314 #id from members table         
         - Request body Subject to change once a working model is in place
         - Post Method'''
        
    #Prediction Pipe
    # Calls function to get data from database according to id provided
    results = db_manager.set_variables(guest_info.member_id)

    # Loads the pickled Model 
    # a new model can be serialize from the Data Exploration notebook
    # Readme file has more information on why the module was not implemented here. 
    random_forest_pipe = load('app/assets/randomforest_modelv3.pkl') #loads pickled model (using loblib)
    
    # df = guest_info.to_df()
    # Converts the dictionary to dataframe
    X = pd.DataFrame(results)
    # Renames the columns to the column names needed for the model. 
    X.rename(columns={'case_members':'CaseMembers', 'race':'Race', 'ethnicity':'Ethnicity', 
                      'current_age':'Current Age', 'gender':'Gender','length_of_stay':'Length of Stay',
                      'enrollment_length':'Days Enrolled in Project', 'household_type':'Household Type',
                      'barrier_count_entry':'Barrier Count at Entry'},inplace=True)
    # Predicts exit destination
    y_pred = random_forest_pipe.predict(X)

    # feature Importances
    # Shows which feature has the most weight on the prediction
    model = random_forest_pipe.named_steps['classifier']
    encoder = random_forest_pipe.named_steps['ord']
    encoded_columns = encoder.transform(X).columns
    importances = pd.Series(model.feature_importances_,encoded_columns)
    top_feats = importances.sort_values(ascending=False)[:3]
    feats = {}
    for k,v in top_feats.items():
        feats[k] = v

    return { 
        'member_id': guest_info.member_id,
        'exit_strategy': y_pred[0],
        'top_features': feats
    }