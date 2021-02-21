
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from sqlalchemy import Column, Integer, String, Date, ForeignKey, BigInteger
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


# Create an instance of this for every db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'

    id = Column(BigInteger, primary_key=True)
    # check_in = Column(JSON)
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


class Family(Base):
    __tablename__ = 'families'

    id = Column(BigInteger, primary_key=True)
    # user_id = Column(String)
    # case_number = Column(Integer)
    # phone_one = Column(JSON)
    # phone_two = Column(JSON)
    # safe_alternate = Column(JSON)
    # emergencyContact = Column(JSON)
    # vehicle = Column(JSON)
    # last_permanent_address = Column(String)
    homeless_info = Column(JSONB)
    # gov_benefits = Column(JSON)
    insurance = Column(JSONB)
    domestic_violence_info = Column(JSONB)
    # pets = Column(JSON)
    # avatar_url = Column(String)
    # percent_complete = Column(Integer)



Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)