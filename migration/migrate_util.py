"""Database connection and models intended to *mostly* mirror the actual web
app database structure. As that structure is prone to change, I built this in
order to get a head start without messing with the web team. 

All columns from actual structure (in its last observed state) are listed, but
some are commented out if there was no obvious parallel in the historical data.

See migration.py for implementation.
"""


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from sqlalchemy import Column, Integer, String, Date, ForeignKey, BigInteger, JSON
from sqlalchemy.dialects.postgresql import JSONB



# Necessary for dropping tables in Postgres
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


load_dotenv()
SQLALCHEMY_DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'

    id = Column(BigInteger, primary_key=True)
    # check_in = Column(JSONB)
    date_of_enrollment = Column(Date)
    household_type = Column(String)
    length_of_stay = Column(Integer)    ## Existing is string
    demographics = Column(JSONB)
    barriers = Column(JSONB)
    schools = Column(JSONB)
    case_members = Column(Integer)
    predicted_exit_destination = Column(String)
    # flag = Column(String)
    # percent_complete = Column(Integer)

    family = relationship('Family', backref=backref('members', lazy=True))
    family_id = Column(BigInteger, ForeignKey('families.id'), nullable=False)

    # NOT IN ORIGINAL - FOR KPIS
    date_of_exit = Column(Date)
    income_at_exit = Column(Integer)
    exit_destination = Column(String)



class Family(Base):
    __tablename__ = 'families'

    id = Column(BigInteger, primary_key=True)
    # user_id = Column(String)
    # case_number = Column(Integer)
    # phone_one = Column(JSONB)
    # phone_two = Column(JSONB)
    # safe_alternate = Column(JSONB)
    # emergencyContact = Column(JSONB)
    # vehicle = Column(JSONB)
    # last_permanent_address = Column(String)
    homeless_info = Column(JSONB)
    # gov_benefits = Column(JSONB)
    insurance = Column(JSONB)
    domestic_violence_info = Column(JSONB)
    # pets = Column(JSONB)
    # avatar_url = Column(String)
    # percent_complete = Column(Integer)



Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)



EXIT_DICT = {    
    # Permanent Exits
    'Staying or living with family, permanent tenure' : 'Permanent Exit',
    'Staying or living with friends, permanent tenure' : 'Permanent Exit',
    'Permanent housing (other than RRH) for formerly homeless persons' : 'Permanent Exit',
    'Rental by client with RRH or equivalent subsidy' : 'Permanent Exit',
    'Rental by client, no ongoing housing subsidy' : 'Permanent Exit',
    'Rental by client, other ongoing housing subsidy' : 'Permanent Exit',
    'Owned by client, no ongoing housing subsidy' : 'Permanent Exit',
    
    # Temporary Exits
    'Staying or living with family, temporary tenure (e.g., room, apartment or house)' : 'Temporary Exit',
    'Staying or living with friends, temporary tenure (e.g., room, apartment or house)' : 'Temporary Exit',
    
    # Emergency Shelter
    'Emergency shelter, including hotel or motel paid for with emergency shelter voucher, or RHY-funded Host Home shelter' : 'Emergency Shelter',
   
    # Transitional Housing
    'Transitional Housing for homeless persons (including homeless youth)' : 'Transitional Housing',
    'Safe Haven' : 'Transitional Housing',
    'Substance Abuse Treatment or Detox Center' : 'Transitional Housing',
    'Foster Care Home or Foster Care Group Home' : 'Transitional Housing',
    'Psychiatric Hospital or Other Psychiatric Facility' : 'Transitional Housing',
   
    # Unknown/Other
    'Hotel or Motel paid for without Emergency Shelter Voucher' : 'Unknown/Other',
    'Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)' : 'Unknown/Other',
    'No exit interview completed' : 'Unknown/Other',
    'Client refused' : 'Unknown/Other',
    'Other' : 'Unknown/Other',
    'Client doesn\'t know' : 'Unknown/Other',
    '' : 'Unknown/Other'
}