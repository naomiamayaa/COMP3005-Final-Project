# COMP3005 Final Project: Health and Fitness Club Management System

## Project Overview

The objective of this project is to design and implement a functional Health and Fitness Club Management System that operates as a centralized, database-driven platform for managing the daily activities and operations of a modern fitness center.

## Features

### Member Management
- Member registration and profile management
- Class registration and scheduling
- Personal training session booking
- Billing and payment tracking
- Fitness goals and health metrics tracking

### Trainer Management
- Trainer profiles with specializations and certifications
- Class scheduling and management
- Personal training session scheduling
- Availability management
- Workload tracking

### Administrative Functions
- Room and equipment management
- Equipment maintenance scheduling
- Class management and monitoring
- Billing and payment processing
- Comprehensive reporting and analytics

### Reports and Analytics
- Room utilization reports
- Popular classes analysis
- Trainer workload reports
- Membership statistics
- Class attendance tracking

## Technology Stack

- **Database**: PostgreSQL 12+
- **Backend**: Python 3.8+
- **Libraries**:
  - psycopg2-binary (PostgreSQL adapter)
  - python-dotenv (Environment configuration)
  - tabulate (Console output formatting)

## Project Structure

```
COMP3005-Final-Project/
├── sql/
│   ├── schema.sql           # Database schema (DDL)
│   ├── sample_data.sql      # Sample data for testing
│   └── queries.sql          # Useful views and queries
├── src/
│   ├── database.py          # Database connection management
│   ├── member_operations.py # Member-related operations
│   ├── trainer_operations.py# Trainer-related operations
│   ├── admin_operations.py  # Administrative operations
│   └── main.py             # Main application interface
├── docs/
│   └── DATABASE_SETUP.md   # Database setup guide
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Installation

### Prerequisites

1. PostgreSQL 12 or higher
2. Python 3.8 or higher
3. pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/naomiamayaa/COMP3005-Final-Project.git
cd COMP3005-Final-Project
```

### Step 2: Set Up Database

1. Create the PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE fitness_club;
\q
```

2. Run the schema creation script:
```bash
psql -U postgres -d fitness_club -f sql/schema.sql
```

3. (Optional) Load sample data:
```bash
psql -U postgres -d fitness_club -f sql/sample_data.sql
```

4. Create views and queries:
```bash
psql -U postgres -d fitness_club -f sql/queries.sql
```

For detailed database setup instructions, see [DATABASE_SETUP.md](docs/DATABASE_SETUP.md).

### Step 3: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fitness_club
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
cd src
python main.py
```

### Main Menu Options

1. **Member Operations**
   - View all members
   - Add new member
   - View member details
   - Update member profile
   - Register for class
   - View member schedule
   - View billing history

2. **Trainer Operations**
   - View all trainers
   - Add new trainer
   - View trainer schedule
   - Schedule class
   - Schedule personal training session
   - View personal training sessions

3. **Admin Operations**
   - Room management
   - Equipment management
   - Class management
   - Billing management

4. **Reports and Analytics**
   - Room utilization
   - Popular classes
   - Trainer workload
   - Membership statistics
   - Class attendance stats

## Database Schema

### Key Tables

- **Person**: Base table for all users
- **Member**: Member-specific information
- **Trainer**: Trainer-specific information
- **AdminStaff**: Administrative staff information
- **Room**: Fitness club rooms/studios
- **Equipment**: Gym equipment tracking
- **FitnessClass**: Scheduled fitness classes
- **ClassRegistration**: Member class registrations
- **PersonalTrainingSession**: One-on-one training sessions
- **Billing**: Payment and billing records

### Key Relationships

- Members can register for multiple classes (many-to-many via ClassRegistration)
- Trainers can teach multiple classes (one-to-many)
- Members can book multiple personal training sessions (many-to-many with Trainer)
- Rooms host multiple classes (one-to-many)
- Members have multiple billing records (one-to-many)

## Sample Data

The system includes sample data with:
- 5 members with different membership types
- 3 trainers with various specializations
- 2 admin staff members
- 5 rooms with different capacities
- 7 pieces of equipment
- 5 fitness classes
- Multiple class registrations
- Personal training sessions
- Billing records

## Development

### Code Structure

- **database.py**: Handles database connections using connection pooling
- **member_operations.py**: All member-related CRUD operations
- **trainer_operations.py**: All trainer-related operations
- **admin_operations.py**: Administrative and management operations
- **main.py**: Command-line interface for the system

### Adding New Features

1. Add database operations to the appropriate operations module
2. Add menu options in main.py
3. Update documentation

## Contributing

This is an academic project for COMP3005. Please follow the course guidelines for contributions.

## License

This project is created for educational purposes as part of COMP3005 coursework.

## Authors

- Course: COMP3005
- Institution: [Your Institution]
- Academic Year: 2024

## Support

For issues or questions:
1. Check the [DATABASE_SETUP.md](docs/DATABASE_SETUP.md) guide
2. Review the SQL scripts in the `sql/` directory
3. Check the Python modules in the `src/` directory

## Acknowledgments

- PostgreSQL documentation
- Python psycopg2 library
- COMP3005 course materials and instructors
