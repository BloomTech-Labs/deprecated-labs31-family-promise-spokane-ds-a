# Column Removal Documentation  

### Note: The column names in this document are present after performing the Cleaning Pipeline 1, which removes many artifacts and numbers from the column labels. Run the EDA notebook up through this step to see the dataframe in this version. 
---



The following are columns/features that only contain 1 value. Columns with only 1 value are unusable for modeling as the data feature is universal. Contextually these data points are either resulting from when the data was accessed (e.g., CurrentDate) or data features that do not exist in the intake packet and are null or 0 for all entries. This is because in certain columns the default is 0 and not NaN. 

Columns:   
- 'Organization Name'  
- 'ProjectType'  
- 'Days Enrolled Until RRH Date of Move-in'  
- 'CurrentDate'  
- 'ProgramType'  
- 'ClientID'  
- 'VA Disability Pension'  
- 'Retirement (Social Security)'  
- 'Pension from a Former Job'  
- 'Alimony' 


---


The following are columns/features that do not appear in the intake packet. If the data does not exist in the current intake packet, the data won't exist in deployment even if it does exist in the training data. Intake packet is the final judge of available data to train on. It must exist there. However some data fields get populated later on, and may be used to predict on at a later date, such as the Bed Night Count

Columns:  
- 'Utilization Tracking Method (Invalid)'
- 'Federal Grant Programs'
- 'Client Location'
- 'Engagement Date'
- 'Days Enrolled Until Engagement Date'
- 'RRH | Most Recent Enrollment'
- 'Coordinated Entry | Most Recent Enrollment'
- 'Emergency Shelter | Most Recent Enrollment'
- 'Bed Nights During Report Period'
- 'Count of Bed Nights - Entire Episode'
- 'Chronic Homeless Status_vHMISDatAssessment'
- 'Chronic Homeless Status_EvaluatevHMIS&HMISDA'



---

The following are columns/features in the provided data that do appear in the intake packet; however, they are not useful for modeling. Each one of these will have rationale provided. 

Columns:  
- 'Current Age'
    - Is age of guests at time of data access from database, not enrollment in shelter
- 'Birthdate Quality'
    - Birthdate is required information, completeness will not be a contributing factor
- 'Information Release Status'
    - Not clearly defined in intake, class baselines are highly skewed. Information regarding privacy status not being used. 
- 'InfoReleaseNo'
    - Information regarding privacy status not being used.
- 'Client Record Restricted'
    - Information regarding privacy status not being used.
- 'Contact Services'
    - Not interpretable, no direct correspondant in data dictionary
- 'Date of Last Contact (Beta)'
    - Not directly in intake packet, however open to exploration by tracking how long since last communication, but it doesn't seem useful.
- 'Date of First Contact (Beta)'
    - Same as 'Date of Last Contact (Beta)'
- 'Chronic Homeless Status'
    - Not directly in intake packet; however, the context is conveyed by information regarding homelessness in past X months/years
- 'Exit Destination'
    - The values in this column have been recontextualized in terms of the five labels used for target prediction. "Target Exit Destinaton"

---


Below are copies of the above lists already formatted into a python list.  

```python
not_in_intake = ['Utilization Tracking Method (Invalid)',
                 'Federal Grant Programs',
                 'Client Location',
                 'Engagement Date',
                 'Days Enrolled Until Engagement Date',
                 'RRH | Most Recent Enrollment',
                 'Coordinated Entry | Most Recent Enrollment',
                 'Emergency Shelter | Most Recent Enrollment',
                 'Bed Nights During Report Period',
                 'Count of Bed Nights - Entire Episode',
                 'Chronic Homeless Status_vHMISDatAssessment',
                 'Chronic Homeless Status_EvaluatevHMIS&HMISDA']


Need Testing:   
['School Status', 'Date of Last ES Stay (Beta)', 'Date of First ES Stay (Beta)', 
'Non-Cash Benefit Count', 'Non-Cash Benefit Count at Exit']```