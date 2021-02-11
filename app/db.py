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

def get_member(db: Session, id: int):
    return db.query(Member).filter(Member.id == id).first()

def get_family(db: Session, id: int):
    return db.query(Family).filter(Family.id == id).first()