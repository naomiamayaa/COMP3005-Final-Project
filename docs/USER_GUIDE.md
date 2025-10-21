# User Guide - Health and Fitness Club Management System

## Table of Contents
1. [Getting Started](#getting-started)
2. [Member Operations](#member-operations)
3. [Trainer Operations](#trainer-operations)
4. [Admin Operations](#admin-operations)
5. [Reports and Analytics](#reports-and-analytics)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Launching the Application

1. Open a terminal/command prompt
2. Navigate to the `src` directory:
   ```bash
   cd /path/to/COMP3005-Final-Project/src
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Main Menu

Upon launch, you'll see the main menu with four options:
- Member Operations
- Trainer Operations
- Admin Operations
- Reports and Analytics

Navigate by entering the number corresponding to your choice.

## Member Operations

### Adding a New Member

1. Select `1. Member Operations` from the main menu
2. Select `2. Add new member`
3. Enter the following information when prompted:
   - First Name
   - Last Name
   - Email (must be unique)
   - Phone number
   - Date of Birth (format: YYYY-MM-DD)
   - Membership Type (Basic/Premium/VIP)
   - Membership Start Date (format: YYYY-MM-DD)
   - Fitness Goals

Example:
```
First Name: John
Last Name: Doe
Email: john.doe@email.com
Phone: 613-555-0123
Date of Birth: 1990-05-15
Membership Type: Premium
Membership Start Date: 2024-01-01
Fitness Goals: Build muscle and improve endurance
```

### Viewing Member Details

1. Select `3. View member details`
2. Enter the Member ID
3. The system displays complete member information

### Registering for a Class

1. Select `5. Register for class`
2. View the list of upcoming classes with available spots
3. Enter your Member ID
4. Enter the Class ID you want to register for
5. Confirmation message will be displayed

**Note**: You cannot register for a full class.

### Viewing Member Schedule

1. Select `6. View member schedule`
2. Enter the Member ID
3. View all scheduled classes including:
   - Class name
   - Date and time
   - Room location
   - Registration status

### Viewing Billing History

1. Select `7. View billing history`
2. Enter the Member ID
3. View all billing records including:
   - Billing date
   - Amount
   - Description
   - Payment status
   - Payment date (if paid)

## Trainer Operations

### Adding a New Trainer

1. Select `2. Trainer Operations` from the main menu
2. Select `2. Add new trainer`
3. Enter the following information:
   - First Name
   - Last Name
   - Email (must be unique)
   - Phone number
   - Date of Birth (format: YYYY-MM-DD)
   - Specialization (e.g., "Strength Training")
   - Certification (e.g., "Certified Personal Trainer (CPT)")
   - Hourly Rate (e.g., 75.00)

### Scheduling a Fitness Class

1. Select `4. Schedule class`
2. Enter the following information:
   - Class Name
   - Description
   - Trainer ID
   - Room ID
   - Date (YYYY-MM-DD)
   - Start Time (HH:MM)
   - End Time (HH:MM)
   - Max Participants

Example:
```
Class Name: Morning Yoga
Description: Energizing yoga flow to start your day
Trainer ID: 1
Room ID: 1
Date: 2024-10-30
Start Time: 07:00
End Time: 08:00
Max Participants: 25
```

### Scheduling a Personal Training Session

1. Select `5. Schedule personal training session`
2. Enter:
   - Member ID
   - Trainer ID
   - Date (YYYY-MM-DD)
   - Start Time (HH:MM)
   - End Time (HH:MM)
   - Notes (optional)

### Viewing Trainer Schedule

1. Select `3. View trainer schedule`
2. Enter the Trainer ID
3. View all scheduled classes including participants count

### Viewing Personal Training Sessions

1. Select `6. View personal training sessions`
2. Enter the Trainer ID
3. View all scheduled personal training sessions with member details

## Admin Operations

### Room Management

1. Select `3. Admin Operations` from the main menu
2. Select `1. Room Management`
3. View all rooms with:
   - Room ID
   - Room Name
   - Capacity
   - Current Status

**Room Status Options**:
- Available: Room is ready for use
- Occupied: Room is currently in use
- Maintenance: Room is under maintenance

### Equipment Management

1. Select `2. Equipment Management`
2. View all equipment with:
   - Equipment ID
   - Name
   - Type
   - Status
   - Next maintenance date

**Equipment Status Options**:
- Operational: Equipment is working properly
- Under Maintenance: Equipment is being serviced
- Out of Service: Equipment is not available

### Class Management

1. Select `3. Class Management`
2. View all upcoming classes with:
   - Class ID
   - Class name
   - Date and time
   - Trainer name
   - Current participants / Max participants

### Billing Management

1. Select `4. Billing Management`
2. View billing summary for all members showing:
   - Total bills
   - Total amount paid
   - Pending payments
   - Overdue payments

## Reports and Analytics

### Room Utilization Report

Shows how frequently each room is being used:
- Room capacity
- Number of scheduled classes
- Current status

Use this to:
- Identify underutilized rooms
- Plan room expansions
- Schedule maintenance during low-usage periods

### Popular Classes Report

Displays classes by popularity:
- Total registrations
- Average participants per class

Use this to:
- Determine which classes to offer more frequently
- Identify trainer strengths
- Plan class schedules

### Trainer Workload Report

Shows each trainer's current workload:
- Number of scheduled classes
- Number of personal training sessions

Use this to:
- Balance workload across trainers
- Identify when to hire additional staff
- Plan trainer schedules

### Membership Statistics

Displays member distribution by membership type:
- Basic membership count
- Premium membership count
- VIP membership count

Use this to:
- Understand membership trends
- Plan pricing strategies
- Forecast revenue

### Class Attendance Stats

Shows attendance rates for classes:
- Registered count
- Attended count
- Attendance percentage

Use this to:
- Monitor class quality
- Identify popular time slots
- Evaluate trainer performance

## Common Tasks

### Cancelling a Class Registration

1. Go to Member Operations
2. Select the appropriate member
3. Use the cancel registration option
4. This will free up a spot for other members

### Updating Member Information

1. Go to Member Operations
2. Select `4. Update member profile`
3. Enter Member ID
4. Enter new values for fields you want to update
5. Press Enter to skip fields you don't want to change

### Processing a Payment

1. Go to Admin Operations
2. Select Billing Management
3. Identify the billing record
4. Update payment status to "Paid"
5. Record payment date

### Scheduling Equipment Maintenance

1. Go to Admin Operations
2. Select Equipment Management
3. Identify equipment needing maintenance
4. Update status to "Under Maintenance"
5. Schedule next maintenance date

## Troubleshooting

### Database Connection Error

**Problem**: "Error creating connection pool"

**Solution**:
1. Check if PostgreSQL is running
2. Verify credentials in `.env` file
3. Ensure database exists: `psql -U postgres -l`
4. Test connection: `psql -U postgres -d fitness_club`

### Cannot Register for Class

**Problem**: "Class is full"

**Solution**:
- The class has reached maximum capacity
- Try a different time slot
- Contact admin to add more sessions

### Duplicate Email Error

**Problem**: Cannot add member/trainer with existing email

**Solution**:
- Each person must have a unique email
- Use a different email address
- Check if the person already exists in the system

### Invalid Date Format

**Problem**: Date not accepted

**Solution**:
- Use YYYY-MM-DD format (e.g., 2024-10-30)
- Ensure the date is valid (e.g., not February 30)
- For times, use HH:MM format (e.g., 14:30)

### Session Timeout

**Problem**: Application becomes unresponsive

**Solution**:
1. Press Ctrl+C to stop the application
2. Restart the application
3. If problem persists, check database connection

## Tips for Efficient Use

1. **Use Reports Regularly**: Check reports to make informed decisions
2. **Update Information Promptly**: Keep member and trainer information current
3. **Monitor Class Capacity**: Register early for popular classes
4. **Schedule Maintenance**: Regularly check equipment maintenance schedules
5. **Review Billing**: Process payments promptly to avoid overdue status

## Getting Help

For technical issues:
1. Check the DATABASE_SETUP.md for database-related problems
2. Review error messages carefully
3. Ensure all required fields are filled correctly
4. Verify data formats (dates, times, etc.)

For feature requests or bugs:
1. Document the issue clearly
2. Include steps to reproduce
3. Note any error messages
4. Contact system administrator
