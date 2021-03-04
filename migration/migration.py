"""Approximate migration of historical data into a temp database. Kept
separate from actual web app database to avoid messing with web team as they
update the structure.

Use caution as this will overwrite any database you connect it to!

First put database url in .env as DATABASE_URL.
"""


from sqlalchemy.exc import DataError

import pandas as pd
from migrate_util import SessionLocal, Member, Family, EXIT_DICT


# JSON cannot store NaNs, so these columns must be singled out and filled with 
# appropriate values.
JSON_STR_COLS = [
    '3.917 Homeless Start Date', '4.4 Covered by Health Insurance',
    '4.11 Domestic Violence - Currently Fleeing DV?', '3.6 Gender',
    '3.15 Relationship to HoH', '3.4 Race', '3.5 Ethnicity', 
    '4.10 Alcohol Abuse (Substance Abuse)', '4.06 Developmental Disability',
    '4.07 Chronic Health Condition', '4.10 Drug Abuse (Substance Abuse)',
    '4.08 HIV/AIDS', '4.09 Mental Health Problem', '4.05 Physical Disability',
    'R5 School Status', '3.12 Exit Destination'
]
JSON_NUM_COLS = [
    '4.2 Income Total at Entry', '4.2 Income Total at Exit'
]


if __name__ == '__main__':
    print('reading csv...')
    df = pd.read_csv('All_data_with_exits.csv', parse_dates=['3.10 Enroll Date', '3.11 Exit Date'])


    print('wrangling...')
    df[JSON_NUM_COLS] = df[JSON_NUM_COLS].fillna(-1)
    df[JSON_STR_COLS] = df[JSON_STR_COLS].fillna('')

    # Look only at HoHs for family data.
    heads = df[df['3.15 Relationship to HoH'] == 'Self']


    print('migrating families...')
    db = SessionLocal()
    for idx in heads.index:
        head = heads.loc[idx]
        family = Family(
            id = int(head['5.9 Household ID']),
            homeless_info = {
                # JSON cannot hold datetime
                'homeless_start_date':head['3.917 Homeless Start Date']
            },
            insurance = {
                'has_insurance':head['4.4 Covered by Health Insurance']
            },
            domestic_violence_info = {
                'fleeing_dv':head['4.11 Domestic Violence - Currently Fleeing DV?']
            }
        )
        db.add(family)
        db.commit()


    print('migrating members...')
    for idx in df.index:
        row = df.loc[idx]
        mem_id = int(row['5.8 Personal ID'])

        # Check if id already exists (there are id repeats in historical data).
        if not db.query(Member).filter(Member.id==mem_id).first():
            member = Member(
                id = mem_id,
                date_of_enrollment = row['3.10 Enroll Date'],
                household_type = row['Household Type'],
                length_of_stay = (row['3.11 Exit Date'] - row['3.10 Enroll Date']).days,
                demographics = {
                    'gender':row['3.6 Gender'],
                    'relationship':row['3.15 Relationship to HoH'],
                    'income':float(row['4.2 Income Total at Entry']),
                    'race':row['3.4 Race'],
                    'ethnicity':row['3.5 Ethnicity']
                },
                barriers = {
                    'alcohol_abuse':row['4.10 Alcohol Abuse (Substance Abuse)'],
                    'developmental_disabilities':row['4.06 Developmental Disability'],
                    'chronic_health_issues':row['4.07 Chronic Health Condition'],
                    'drug_abuse':row['4.10 Drug Abuse (Substance Abuse)'],
                    'HIV_AIDs':row['4.08 HIV/AIDS'],
                    'mental_illness':row['4.09 Mental Health Problem'],
                    'physical_disabilities':row['4.05 Physical Disability'],
                },
                schools = {
                    'enrolled_status':row['R5 School Status'],
                },
                case_members = int(row['CaseMembers']),
                date_of_exit = row['3.11 Exit Date'],
                income_at_exit = float(row['4.2 Income Total at Exit']),
                exit_destination = EXIT_DICT[row['3.12 Exit Destination']]
            )
            family = db.query(Family).filter(Family.id==int(row['5.9 Household ID'])).first()
            if family:
                family.members.append(member)

            # Postgres throws a weird error about integers being too big, even though
            # none of the integer values in this data are above 150,000. Since this is
            # only a test migration I simply ignored those member rows which threw the 
            # error.
            try:
                db.commit()
            except DataError:
                db.rollback()
                print('DataError on', mem_id)

    print('done!')
    print(db.query(Family).count(), 'families.')
    print(db.query(Member).count(), 'members.')
    db.close()