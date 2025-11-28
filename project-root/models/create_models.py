# create_tables.py
from models.database import engine, Base
import models.models  # noqa: F401  # ensures models are imported and registered


def main():
    print("Creating tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    main()
