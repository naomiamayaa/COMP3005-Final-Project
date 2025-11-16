# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load .env from project root
load_dotenv()

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5433")           # your running port
PGDATABASE = os.getenv("PGDATABASE", "fitnessclub")
PGUSER = os.getenv("PGUSER", "naomiamayalovett")
PGPASSWORD = os.getenv("PGPASSWORD", "")

DATABASE_URL = (
    f"postgresql+psycopg://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
)

# echo=True prints SQL – useful while developing
engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
