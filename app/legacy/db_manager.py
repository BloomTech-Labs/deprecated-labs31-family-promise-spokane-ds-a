'''This is the database manager module 
   This file has two functions one connect to the database 
   the other one assigns the variables to be used in the prediction model. '''
#imports
import psycopg2
import psycopg2.extras
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

def dbmanage(uri,query):
      '''Function to connect to the database given a database URI and a query to perform'''
      db_conn = psycopg2.connect(uri)
      db_curs = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      db_curs.execute(query)
      results = db_curs.fetchall()
      db_curs.close()
      db_conn.close()
      return results[0] # Returns only the first results since only firrst is needed

def set_variables(member_id):
  ''' assigns the database values to correct dictionary keys '''
  #current date for Days/ Years calculations
  today_date = datetime.date.today()
  results_dict = {} # Dictionary to hold the results value to be transformed to df
  uri = os.getenv('DB_URL') # enviromental variable Database Credentials 

  # Query used to pull the data from database. 
  # When Using new Model Use the following instead
  # query = 'SELECT * FROM members,families \
  # WHERE id = {} \
  # AND members.family_id = families.id'.format(member_id)
  query = 'SELECT * FROM members where id = {}'.format(member_id)
  results = dbmanage(uri,query)

  #sets variables from the db results
  results_dict['case_members'] = results['case_members']
  results_dict['race'] = results['demographics']['race']
  results_dict['ethnicity'] = results['demographics']['ethnicity']
  results_dict['current_age'] = int((today_date - datetime.datetime.strptime(
      results['demographics']['DOB'], '%m-%d-%Y').date()).days / 365.2425
      )
  results_dict['gender'] = results['demographics']['gender']
  results_dict['length_of_stay'] = results['length_of_stay']
  results_dict['enrollment_length'] = int((today_date - results['date_of_enrollment']).days)
  results_dict['household_type'] = results['household_type']
  results_dict['barrier_count'] = 0 
  # adds 1 for every barrier that is equal to true. 
  for item in results['barriers'].values():
    if item == True:
      results_dict['barrier_count'] += 1
  #returns the final result
  return results_dict
if __name__ == '__main__':
      # Prints the results (Just for debugging) 
    print(set_variables(2))
    results = set_variables(2)
    print('Case Members',results['case_members'])
    print('ethnicity',results['ethnicity'])
    print('race',results['race'])
    print('current age',results['current_age'])
    print('gender',results['gender'])
    print('length_of_stay',results['length_of_stay'])
    print('enrollment_length',results['enrollment_length'])
    print('household_type',results['household_type'])
    print('barrier_count',results['barrier_count'])
