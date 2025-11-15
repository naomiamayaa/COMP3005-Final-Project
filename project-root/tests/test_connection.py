from dotenv import load_dotenv
import psycopg
import os

load_dotenv()  # load values from .env

try:
    conn = psycopg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )
    print("SUCCESS: Connected to database!")
    conn.close()
except Exception as e:
    print("FAILED to connect:", e)
