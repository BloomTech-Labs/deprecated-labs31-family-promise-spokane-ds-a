"""Functions for initiating database connection and making various queries."""

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()
SQLALCHEMY_DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Build models from existing tables

Base = automap_base()
Base.prepare(engine, reflect=True)

Member = Base.classes.members
Family = Base.classes.families