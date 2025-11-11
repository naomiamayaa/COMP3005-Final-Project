# 🏋️‍♀️ Health & Fitness Club Management System  
### COMP 3005 – Final Project (Fall 2025)

The objective of this project is to design and implement a functional Health and Fitness Club Management System that operates as a centralized, database‑driven platform for managing the daily activities and operations of a modern fitness center. 

This database-driven management system is built using **Python**, **SQLAlchemy (ORM)**, and **PostgreSQL**.  
The supports **Members**, **Trainers**, and **Administrators**, allowing scheduling, availability management, and goal and equipment tracking.

## 1. Team Onboarding & Local Setup Guide

### Prerequisites
Each team member needs:
- **Python 3.10+**
- **PostgreSQL 14+** (via Postgres.app or Homebrew)   
- **VS Code** with these extensions:
  - `ms-python.python`
  - `mtxr.sqltools`
  - `mtxr.sqltools-driver-pg`

## 2. Clone the project
`git clone <your_repo_url>`
`cd COMP3005-Final-Project`

## 3. Set up venv
`python3 -m venv venv`
`source venv/bin/activate`

## 4. install dependencies
`pip install -r requirements.txt`

## 5. Create your .env file
Each team member creates a local .env file inside the project-root/ folder:

`PGHOST=localhost
PGPORT=5432
PGDATABASE=fitnessclub
PGUSER=<your_postgres_username>
PGPASSWORD=<your_postgres_password>`

The .env file is ignored by Git to keep credentials private.

Test your connection:
`psql -d fitnessclub`

if the database doesn't exist, create it:
`createdb fitnessclub`

## 6. Initialize the database
Run your ORM setup script to create all tables:
`cd project-root`
`python3 -m app.init_db`

Expected output:
`Creating all tables...
INFO sqlalchemy.engine.Engine CREATE TABLE ...
Done.`

## 7. Run the app
`source venv/bin/activate`
`cd project-root`
`python3 -m app.main`

## Environment Summary
- .env	Local database credentials (ignored by Git)
- .gitignore	Prevents .env and venv/ from syncing
- db/database.py	Loads .env variables with python-dotenv
- models/	ORM entity definitions
- app/	CLI logic for Members, Trainers
- Admins
docs/	ERD + report for submission
