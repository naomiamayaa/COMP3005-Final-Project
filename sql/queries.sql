-- Useful Queries and Views for Health and Fitness Club Management System
-- COMP3005 Final Project

-- View: Complete Member Information
CREATE OR REPLACE VIEW MemberDetails AS
SELECT 
    m.member_id,
    p.first_name,
    p.last_name,
    p.email,
    p.phone,
    p.date_of_birth,
    m.membership_type,
    m.membership_start_date,
    m.membership_end_date,
    m.fitness_goals
FROM Member m
JOIN Person p ON m.person_id = p.person_id;

-- View: Complete Trainer Information
CREATE OR REPLACE VIEW TrainerDetails AS
SELECT 
    t.trainer_id,
    p.first_name,
    p.last_name,
    p.email,
    p.phone,
    t.specialization,
    t.certification,
    t.hourly_rate,
    t.available_schedule
FROM Trainer t
JOIN Person p ON t.person_id = p.person_id;

-- View: Upcoming Classes with Details
CREATE OR REPLACE VIEW UpcomingClasses AS
SELECT 
    fc.class_id,
    fc.class_name,
    fc.description,
    fc.class_date,
    fc.start_time,
    fc.end_time,
    p.first_name || ' ' || p.last_name AS trainer_name,
    r.room_name,
    fc.max_participants,
    fc.current_participants,
    (fc.max_participants - fc.current_participants) AS available_spots
FROM FitnessClass fc
LEFT JOIN Trainer t ON fc.trainer_id = t.trainer_id
LEFT JOIN Person p ON t.person_id = p.person_id
LEFT JOIN Room r ON fc.room_id = r.room_id
WHERE fc.class_date >= CURRENT_DATE
ORDER BY fc.class_date, fc.start_time;

-- View: Member Class Schedule
CREATE OR REPLACE VIEW MemberClassSchedule AS
SELECT 
    p.first_name || ' ' || p.last_name AS member_name,
    fc.class_name,
    fc.class_date,
    fc.start_time,
    fc.end_time,
    r.room_name,
    cr.status
FROM ClassRegistration cr
JOIN Member m ON cr.member_id = m.member_id
JOIN Person p ON m.person_id = p.person_id
JOIN FitnessClass fc ON cr.class_id = fc.class_id
LEFT JOIN Room r ON fc.room_id = r.room_id
ORDER BY fc.class_date, fc.start_time;

-- View: Trainer Schedule
CREATE OR REPLACE VIEW TrainerSchedule AS
SELECT 
    p.first_name || ' ' || p.last_name AS trainer_name,
    fc.class_name,
    fc.class_date,
    fc.start_time,
    fc.end_time,
    r.room_name,
    fc.current_participants
FROM FitnessClass fc
JOIN Trainer t ON fc.trainer_id = t.trainer_id
JOIN Person p ON t.person_id = p.person_id
LEFT JOIN Room r ON fc.room_id = r.room_id
WHERE fc.class_date >= CURRENT_DATE
ORDER BY fc.class_date, fc.start_time;

-- View: Personal Training Sessions Schedule
CREATE OR REPLACE VIEW PersonalTrainingSchedule AS
SELECT 
    pts.session_id,
    pm.first_name || ' ' || pm.last_name AS member_name,
    pt.first_name || ' ' || pt.last_name AS trainer_name,
    pts.session_date,
    pts.start_time,
    pts.end_time,
    pts.status,
    pts.notes
FROM PersonalTrainingSession pts
JOIN Member m ON pts.member_id = m.member_id
JOIN Person pm ON m.person_id = pm.person_id
JOIN Trainer t ON pts.trainer_id = t.trainer_id
JOIN Person pt ON t.person_id = pt.person_id
WHERE pts.session_date >= CURRENT_DATE
ORDER BY pts.session_date, pts.start_time;

-- View: Equipment Maintenance Schedule
CREATE OR REPLACE VIEW EquipmentMaintenanceSchedule AS
SELECT 
    equipment_id,
    equipment_name,
    equipment_type,
    last_maintenance_date,
    next_maintenance_date,
    status,
    CASE 
        WHEN next_maintenance_date <= CURRENT_DATE THEN 'Overdue'
        WHEN next_maintenance_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'Due Soon'
        ELSE 'Scheduled'
    END AS maintenance_status
FROM Equipment
ORDER BY next_maintenance_date;

-- View: Member Billing Summary
CREATE OR REPLACE VIEW MemberBillingSummary AS
SELECT 
    m.member_id,
    p.first_name || ' ' || p.last_name AS member_name,
    COUNT(b.billing_id) AS total_bills,
    SUM(CASE WHEN b.payment_status = 'Paid' THEN b.amount ELSE 0 END) AS total_paid,
    SUM(CASE WHEN b.payment_status = 'Pending' THEN b.amount ELSE 0 END) AS total_pending,
    SUM(CASE WHEN b.payment_status = 'Overdue' THEN b.amount ELSE 0 END) AS total_overdue
FROM Member m
JOIN Person p ON m.person_id = p.person_id
LEFT JOIN Billing b ON m.member_id = b.member_id
GROUP BY m.member_id, p.first_name, p.last_name;

-- Query: Find available trainers for a specific time
-- Example usage: Replace the date and time values
-- SELECT * FROM find_available_trainers('2024-10-25', '14:00:00', '15:00:00');

-- Query: Get class attendance statistics
CREATE OR REPLACE VIEW ClassAttendanceStats AS
SELECT 
    fc.class_id,
    fc.class_name,
    fc.class_date,
    fc.max_participants,
    COUNT(cr.registration_id) AS registered_count,
    COUNT(CASE WHEN cr.status = 'Attended' THEN 1 END) AS attended_count,
    ROUND(COUNT(CASE WHEN cr.status = 'Attended' THEN 1 END) * 100.0 / NULLIF(COUNT(cr.registration_id), 0), 2) AS attendance_rate
FROM FitnessClass fc
LEFT JOIN ClassRegistration cr ON fc.class_id = cr.class_id
GROUP BY fc.class_id, fc.class_name, fc.class_date, fc.max_participants
ORDER BY fc.class_date DESC;

-- Query: Room utilization report
CREATE OR REPLACE VIEW RoomUtilization AS
SELECT 
    r.room_id,
    r.room_name,
    r.capacity,
    COUNT(fc.class_id) AS classes_scheduled,
    r.status
FROM Room r
LEFT JOIN FitnessClass fc ON r.room_id = fc.room_id AND fc.class_date >= CURRENT_DATE
GROUP BY r.room_id, r.room_name, r.capacity, r.status
ORDER BY classes_scheduled DESC;

-- Query: Popular classes (most registered)
CREATE OR REPLACE VIEW PopularClasses AS
SELECT 
    fc.class_name,
    COUNT(cr.registration_id) AS total_registrations,
    AVG(fc.current_participants) AS avg_participants
FROM FitnessClass fc
LEFT JOIN ClassRegistration cr ON fc.class_id = cr.class_id
GROUP BY fc.class_name
ORDER BY total_registrations DESC;
