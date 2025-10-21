# Database Setup Guide

## Prerequisites

- PostgreSQL 12 or higher installed
- Database user with CREATE DATABASE privileges

## Installation Steps

### 1. Create Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fitness_club;

# Connect to the database
\c fitness_club
```

### 2. Run Schema Script

Execute the schema creation script:

```bash
psql -U postgres -d fitness_club -f sql/schema.sql
```

This will create all necessary tables:
- Person
- Member
- Trainer
- AdminStaff
- Room
- Equipment
- FitnessClass
- ClassRegistration
- PersonalTrainingSession
- Billing

### 3. Load Sample Data (Optional)

To populate the database with sample data for testing:

```bash
psql -U postgres -d fitness_club -f sql/sample_data.sql
```

### 4. Create Views and Queries

Load the views and utility queries:

```bash
psql -U postgres -d fitness_club -f sql/queries.sql
```

## Database Schema Overview

### Core Tables

#### Person Table
Base table for all users (members, trainers, admin staff)
- `person_id` (Primary Key)
- `first_name`, `last_name`
- `email` (Unique)
- `phone`, `date_of_birth`
- `created_at`

#### Member Table
Stores member-specific information
- `member_id` (Primary Key)
- `person_id` (Foreign Key → Person)
- `membership_type` (Basic, Premium, VIP)
- `membership_start_date`, `membership_end_date`
- `health_metrics` (JSONB)
- `fitness_goals`

#### Trainer Table
Stores trainer-specific information
- `trainer_id` (Primary Key)
- `person_id` (Foreign Key → Person)
- `specialization`, `certification`
- `hourly_rate`
- `available_schedule` (JSONB)

#### Room Table
Fitness club rooms/studios
- `room_id` (Primary Key)
- `room_name`, `capacity`
- `equipment_available`
- `status` (Available, Occupied, Maintenance)

#### Equipment Table
Gym equipment tracking
- `equipment_id` (Primary Key)
- `equipment_name`, `equipment_type`
- `purchase_date`
- `last_maintenance_date`, `next_maintenance_date`
- `status` (Operational, Under Maintenance, Out of Service)

#### FitnessClass Table
Scheduled fitness classes
- `class_id` (Primary Key)
- `class_name`, `description`
- `trainer_id` (Foreign Key → Trainer)
- `room_id` (Foreign Key → Room)
- `class_date`, `start_time`, `end_time`
- `max_participants`, `current_participants`

#### ClassRegistration Table
Member class registrations (Many-to-Many)
- `registration_id` (Primary Key)
- `member_id` (Foreign Key → Member)
- `class_id` (Foreign Key → FitnessClass)
- `registration_date`
- `status` (Registered, Attended, Cancelled)

#### PersonalTrainingSession Table
One-on-one training sessions
- `session_id` (Primary Key)
- `member_id` (Foreign Key → Member)
- `trainer_id` (Foreign Key → Trainer)
- `session_date`, `start_time`, `end_time`
- `status` (Scheduled, Completed, Cancelled)
- `notes`

#### Billing Table
Member billing and payments
- `billing_id` (Primary Key)
- `member_id` (Foreign Key → Member)
- `billing_date`, `amount`
- `description`
- `payment_status` (Pending, Paid, Overdue)
- `payment_date`

### Database Views

The system includes several pre-defined views for common queries:

- **MemberDetails**: Complete member information with person details
- **TrainerDetails**: Complete trainer information with person details
- **UpcomingClasses**: All upcoming fitness classes with availability
- **MemberClassSchedule**: Member's scheduled classes
- **TrainerSchedule**: Trainer's class schedule
- **PersonalTrainingSchedule**: All personal training sessions
- **EquipmentMaintenanceSchedule**: Equipment maintenance tracking
- **MemberBillingSummary**: Billing summary per member
- **ClassAttendanceStats**: Class attendance statistics
- **RoomUtilization**: Room usage statistics
- **PopularClasses**: Most popular classes

## Environment Configuration

Create a `.env` file in the project root:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fitness_club
DB_USER=postgres
DB_PASSWORD=your_password_here
```

## Verification

To verify the setup, run these queries:

```sql
-- Check tables
\dt

-- Check views
\dv

-- Count records in each table
SELECT 'Person' as table_name, COUNT(*) FROM Person
UNION ALL
SELECT 'Member', COUNT(*) FROM Member
UNION ALL
SELECT 'Trainer', COUNT(*) FROM Trainer
UNION ALL
SELECT 'FitnessClass', COUNT(*) FROM FitnessClass;
```

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL service is running
- Check firewall settings
- Verify credentials in `.env` file

### Permission Issues
- Grant necessary privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE fitness_club TO your_username;
```

### Data Integrity Issues
- The schema includes foreign key constraints and check constraints
- Ensure data meets all constraints when inserting
