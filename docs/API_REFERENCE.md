# API Reference - Health and Fitness Club Management System

## Table of Contents
1. [Database Module](#database-module)
2. [Member Operations](#member-operations)
3. [Trainer Operations](#trainer-operations)
4. [Admin Operations](#admin-operations)

---

## Database Module

### DatabaseConnection Class

Manages PostgreSQL connection pool for the application.

#### Methods

##### `__init__()`
Initializes the database connection pool.

**Raises**: `DatabaseError` if connection fails

##### `get_connection()`
Gets a connection from the pool.

**Returns**: PostgreSQL connection object

##### `return_connection(connection)`
Returns a connection to the pool.

**Parameters**:
- `connection`: Connection object to return

##### `close_all_connections()`
Closes all connections in the pool.

### DatabaseManager Class

Provides high-level database operations.

#### Methods

##### `execute_query(query, params=None, fetch=True)`
Execute a SQL query.

**Parameters**:
- `query` (str): SQL query string
- `params` (tuple/dict): Query parameters
- `fetch` (bool): Whether to fetch results

**Returns**: Query results if fetch=True, None otherwise

##### `execute_many(query, params_list)`
Execute a query multiple times with different parameters.

**Parameters**:
- `query` (str): SQL query string
- `params_list` (list): List of parameter tuples

##### `call_procedure(procedure_name, params=None)`
Call a stored procedure.

**Parameters**:
- `procedure_name` (str): Name of the procedure
- `params` (tuple): Procedure parameters

---

## Member Operations

### MemberOperations Class

Manages all member-related database operations.

#### Methods

##### `add_member(first_name, last_name, email, phone, date_of_birth, membership_type, membership_start_date, fitness_goals=None)`

Add a new member to the system.

**Parameters**:
- `first_name` (str): Member's first name
- `last_name` (str): Member's last name
- `email` (str): Member's email (must be unique)
- `phone` (str): Member's phone number
- `date_of_birth` (str/date): Member's date of birth
- `membership_type` (str): Type of membership ('Basic', 'Premium', 'VIP')
- `membership_start_date` (str/date): Start date of membership
- `fitness_goals` (str, optional): Member's fitness goals

**Returns**: `member_id` (int) of the newly created member

**Raises**: `Exception` if email already exists or invalid data

**Example**:
```python
member_id = member_ops.add_member(
    'John', 'Doe', 'john@email.com', '613-555-0123',
    '1990-05-15', 'Premium', '2024-01-01',
    'Build muscle and improve endurance'
)
```

##### `get_member_by_id(member_id)`

Get member details by member ID.

**Parameters**:
- `member_id` (int): Member's ID

**Returns**: Dictionary with member details or None if not found

**Example**:
```python
member = member_ops.get_member_by_id(1)
print(f"Member: {member['first_name']} {member['last_name']}")
```

##### `get_all_members()`

Get all members.

**Returns**: List of dictionaries, each containing member details

##### `update_member_profile(member_id, **kwargs)`

Update member profile information.

**Parameters**:
- `member_id` (int): Member's ID
- `**kwargs`: Fields to update (email, phone, fitness_goals, etc.)

**Valid fields**:
- Person fields: first_name, last_name, email, phone, date_of_birth
- Member fields: membership_type, fitness_goals, health_metrics

**Example**:
```python
member_ops.update_member_profile(
    1,
    email='newemail@email.com',
    fitness_goals='Marathon training'
)
```

##### `register_for_class(member_id, class_id)`

Register a member for a fitness class.

**Parameters**:
- `member_id` (int): Member's ID
- `class_id` (int): Class ID

**Returns**: `registration_id` (int)

**Raises**: `ValueError` if class is full or not found

##### `cancel_class_registration(member_id, class_id)`

Cancel a class registration.

**Parameters**:
- `member_id` (int): Member's ID
- `class_id` (int): Class ID

##### `get_member_schedule(member_id)`

Get a member's class schedule.

**Parameters**:
- `member_id` (int): Member's ID

**Returns**: List of scheduled classes with details

##### `get_member_billing_history(member_id)`

Get a member's billing history.

**Parameters**:
- `member_id` (int): Member's ID

**Returns**: List of billing records

---

## Trainer Operations

### TrainerOperations Class

Manages all trainer-related database operations.

#### Methods

##### `add_trainer(first_name, last_name, email, phone, date_of_birth, specialization, certification, hourly_rate, available_schedule=None)`

Add a new trainer to the system.

**Parameters**:
- `first_name` (str): Trainer's first name
- `last_name` (str): Trainer's last name
- `email` (str): Trainer's email (must be unique)
- `phone` (str): Trainer's phone number
- `date_of_birth` (str/date): Trainer's date of birth
- `specialization` (str): Trainer's area of specialization
- `certification` (str): Trainer's certifications
- `hourly_rate` (float): Trainer's hourly rate
- `available_schedule` (dict, optional): JSON object with availability

**Returns**: `trainer_id` (int) of the newly created trainer

**Example**:
```python
trainer_id = trainer_ops.add_trainer(
    'Jane', 'Smith', 'jane@email.com', '613-555-0124',
    '1985-03-20', 'Yoga', 'RYT-200', 65.00
)
```

##### `get_trainer_by_id(trainer_id)`

Get trainer details by trainer ID.

**Parameters**:
- `trainer_id` (int): Trainer's ID

**Returns**: Dictionary with trainer details or None if not found

##### `get_all_trainers()`

Get all trainers.

**Returns**: List of dictionaries, each containing trainer details

##### `update_trainer_profile(trainer_id, **kwargs)`

Update trainer profile information.

**Parameters**:
- `trainer_id` (int): Trainer's ID
- `**kwargs`: Fields to update

##### `get_trainer_schedule(trainer_id)`

Get a trainer's schedule.

**Parameters**:
- `trainer_id` (int): Trainer's ID

**Returns**: List of scheduled classes

##### `get_trainer_personal_sessions(trainer_id)`

Get a trainer's personal training sessions.

**Parameters**:
- `trainer_id` (int): Trainer's ID

**Returns**: List of personal training sessions

##### `add_class(class_name, description, trainer_id, room_id, class_date, start_time, end_time, max_participants=20)`

Add a new fitness class.

**Parameters**:
- `class_name` (str): Name of the class
- `description` (str): Class description
- `trainer_id` (int): Trainer's ID
- `room_id` (int): Room ID
- `class_date` (str/date): Date of the class
- `start_time` (str/time): Start time
- `end_time` (str/time): End time
- `max_participants` (int, optional): Maximum participants (default: 20)

**Returns**: `class_id` (int) of the newly created class

**Example**:
```python
class_id = trainer_ops.add_class(
    'Morning Yoga', 'Energizing flow',
    1, 1, '2024-10-30', '07:00', '08:00', 25
)
```

##### `schedule_personal_session(member_id, trainer_id, session_date, start_time, end_time, notes=None)`

Schedule a personal training session.

**Parameters**:
- `member_id` (int): Member's ID
- `trainer_id` (int): Trainer's ID
- `session_date` (str/date): Date of session
- `start_time` (str/time): Start time
- `end_time` (str/time): End time
- `notes` (str, optional): Session notes

**Returns**: `session_id` (int)

##### `update_session_status(session_id, status, notes=None)`

Update personal training session status.

**Parameters**:
- `session_id` (int): Session ID
- `status` (str): New status ('Scheduled', 'Completed', 'Cancelled')
- `notes` (str, optional): Updated notes

---

## Admin Operations

### AdminOperations Class

Manages administrative database operations.

#### Room Management

##### `add_room(room_name, capacity, equipment_available, status='Available')`

Add a new room.

**Parameters**:
- `room_name` (str): Name of the room
- `capacity` (int): Room capacity
- `equipment_available` (str): Description of available equipment
- `status` (str, optional): Room status (default: 'Available')

**Returns**: `room_id` (int)

##### `get_all_rooms()`

Get all rooms.

**Returns**: List of all rooms with details

##### `update_room_status(room_id, status)`

Update room status.

**Parameters**:
- `room_id` (int): Room ID
- `status` (str): New status ('Available', 'Occupied', 'Maintenance')

#### Equipment Management

##### `add_equipment(equipment_name, equipment_type, purchase_date, next_maintenance_date, status='Operational')`

Add new equipment.

**Parameters**:
- `equipment_name` (str): Name of equipment
- `equipment_type` (str): Type of equipment
- `purchase_date` (str/date): Date of purchase
- `next_maintenance_date` (str/date): Next maintenance date
- `status` (str, optional): Equipment status (default: 'Operational')

**Returns**: `equipment_id` (int)

##### `get_all_equipment()`

Get all equipment.

**Returns**: List of all equipment with details

##### `get_equipment_maintenance_schedule()`

Get equipment maintenance schedule.

**Returns**: List of equipment with maintenance information

##### `update_equipment_maintenance(equipment_id, last_maintenance_date, next_maintenance_date)`

Update equipment maintenance dates.

**Parameters**:
- `equipment_id` (int): Equipment ID
- `last_maintenance_date` (str/date): Last maintenance date
- `next_maintenance_date` (str/date): Next maintenance date

##### `update_equipment_status(equipment_id, status)`

Update equipment status.

**Parameters**:
- `equipment_id` (int): Equipment ID
- `status` (str): New status ('Operational', 'Under Maintenance', 'Out of Service')

#### Class Management

##### `get_all_classes()`

Get all fitness classes.

**Returns**: List of all classes with details

##### `get_upcoming_classes()`

Get upcoming fitness classes.

**Returns**: List of upcoming classes

##### `get_class_attendance_stats()`

Get class attendance statistics.

**Returns**: List of classes with attendance data

##### `update_class_attendance(registration_id, status='Attended')`

Update class attendance status.

**Parameters**:
- `registration_id` (int): Registration ID
- `status` (str, optional): New status (default: 'Attended')

#### Billing Management

##### `create_billing_record(member_id, amount, description, billing_date=None, payment_status='Pending')`

Create a billing record.

**Parameters**:
- `member_id` (int): Member ID
- `amount` (float): Billing amount
- `description` (str): Description of charge
- `billing_date` (str/date, optional): Date of billing
- `payment_status` (str, optional): Payment status (default: 'Pending')

**Returns**: `billing_id` (int)

**Example**:
```python
billing_id = admin_ops.create_billing_record(
    1, 99.99, 'Monthly Premium Membership Fee'
)
```

##### `update_payment_status(billing_id, payment_status, payment_date=None)`

Update payment status.

**Parameters**:
- `billing_id` (int): Billing ID
- `payment_status` (str): New status ('Paid', 'Pending', 'Overdue')
- `payment_date` (str/date, optional): Date of payment

##### `get_all_billing_records()`

Get all billing records.

**Returns**: List of all billing records with member information

##### `get_member_billing_summary()`

Get billing summary for all members.

**Returns**: List of members with billing summary

#### Reports and Analytics

##### `get_room_utilization()`

Get room utilization report.

**Returns**: List of rooms with utilization statistics

##### `get_popular_classes()`

Get popular classes report.

**Returns**: List of classes sorted by popularity

##### `get_trainer_workload()`

Get trainer workload report.

**Returns**: List of trainers with workload statistics

##### `get_membership_statistics()`

Get membership statistics.

**Returns**: Distribution of members by membership type

---

## Data Types and Constraints

### Membership Types
- `'Basic'`: Basic membership
- `'Premium'`: Premium membership
- `'VIP'`: VIP membership

### Room Status
- `'Available'`: Room is available
- `'Occupied'`: Room is currently in use
- `'Maintenance'`: Room is under maintenance

### Equipment Status
- `'Operational'`: Equipment is working
- `'Under Maintenance'`: Equipment is being serviced
- `'Out of Service'`: Equipment is unavailable

### Registration Status
- `'Registered'`: Active registration
- `'Attended'`: Member attended the class
- `'Cancelled'`: Registration was cancelled

### Session Status
- `'Scheduled'`: Session is scheduled
- `'Completed'`: Session was completed
- `'Cancelled'`: Session was cancelled

### Payment Status
- `'Pending'`: Payment is pending
- `'Paid'`: Payment has been made
- `'Overdue'`: Payment is overdue

---

## Error Handling

All functions may raise exceptions for various error conditions:

- **Database Errors**: Connection issues, query failures
- **Validation Errors**: Invalid data, constraint violations
- **Not Found Errors**: Entity not found in database
- **Duplicate Errors**: Unique constraint violations (e.g., duplicate email)

Always use try-except blocks when calling these functions:

```python
try:
    member_id = member_ops.add_member(...)
except Exception as e:
    print(f"Error: {e}")
```
