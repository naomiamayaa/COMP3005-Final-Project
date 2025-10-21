-- Sample Data for Health and Fitness Club Management System
-- COMP3005 Final Project

-- Insert sample persons
INSERT INTO Person (first_name, last_name, email, phone, date_of_birth) VALUES
('John', 'Smith', 'john.smith@email.com', '613-555-0101', '1990-05-15'),
('Emily', 'Johnson', 'emily.johnson@email.com', '613-555-0102', '1988-08-22'),
('Michael', 'Williams', 'michael.williams@email.com', '613-555-0103', '1992-03-10'),
('Sarah', 'Brown', 'sarah.brown@email.com', '613-555-0104', '1995-11-30'),
('David', 'Jones', 'david.jones@email.com', '613-555-0105', '1985-07-18'),
('Jessica', 'Garcia', 'jessica.garcia@email.com', '613-555-0106', '1993-09-25'),
('Robert', 'Miller', 'robert.miller@email.com', '613-555-0107', '1987-12-05'),
('Lisa', 'Davis', 'lisa.davis@email.com', '613-555-0108', '1991-04-14'),
('James', 'Rodriguez', 'james.rodriguez@email.com', '613-555-0109', '1989-06-20'),
('Amanda', 'Martinez', 'amanda.martinez@email.com', '613-555-0110', '1994-02-28');

-- Insert Members
INSERT INTO Member (person_id, membership_type, membership_start_date, membership_end_date, fitness_goals) VALUES
(1, 'Premium', '2024-01-01', '2024-12-31', 'Build muscle and improve strength'),
(2, 'VIP', '2024-02-15', '2025-02-14', 'Weight loss and cardiovascular health'),
(3, 'Basic', '2024-03-01', '2024-12-31', 'General fitness maintenance'),
(4, 'Premium', '2024-01-15', '2024-12-31', 'Marathon training'),
(5, 'VIP', '2024-04-01', '2025-03-31', 'Overall health and wellness');

-- Insert Trainers
INSERT INTO Trainer (person_id, specialization, certification, hourly_rate, available_schedule) VALUES
(6, 'Strength Training', 'Certified Personal Trainer (CPT)', 75.00, '{"Monday": ["09:00-17:00"], "Wednesday": ["09:00-17:00"], "Friday": ["09:00-17:00"]}'),
(7, 'Yoga and Flexibility', 'RYT-200 Yoga Certification', 65.00, '{"Tuesday": ["10:00-18:00"], "Thursday": ["10:00-18:00"], "Saturday": ["09:00-15:00"]}'),
(8, 'Cardio and HIIT', 'NASM Certified', 70.00, '{"Monday": ["06:00-14:00"], "Tuesday": ["06:00-14:00"], "Wednesday": ["06:00-14:00"]}');

-- Insert Admin Staff
INSERT INTO AdminStaff (person_id, role, hire_date) VALUES
(9, 'Manager', '2023-01-15'),
(10, 'Front Desk', '2023-06-01');

-- Insert Rooms
INSERT INTO Room (room_name, capacity, equipment_available, status) VALUES
('Main Studio', 30, 'Yoga mats, mirrors, sound system', 'Available'),
('Weight Room', 20, 'Free weights, benches, squat racks', 'Available'),
('Cardio Zone', 25, 'Treadmills, ellipticals, stationary bikes', 'Available'),
('Spin Studio', 20, 'Spin bikes, sound system, mirrors', 'Available'),
('Private Training Room', 5, 'Various equipment, adjustable', 'Available');

-- Insert Equipment
INSERT INTO Equipment (equipment_name, equipment_type, purchase_date, last_maintenance_date, next_maintenance_date, status) VALUES
('Treadmill-01', 'Cardio', '2023-01-15', '2024-09-01', '2024-12-01', 'Operational'),
('Treadmill-02', 'Cardio', '2023-01-15', '2024-09-01', '2024-12-01', 'Operational'),
('Elliptical-01', 'Cardio', '2023-02-20', '2024-08-15', '2024-11-15', 'Operational'),
('Stationary Bike-01', 'Cardio', '2023-03-10', '2024-09-10', '2024-12-10', 'Operational'),
('Squat Rack-01', 'Strength', '2023-01-20', '2024-08-01', '2025-02-01', 'Operational'),
('Bench Press-01', 'Strength', '2023-01-20', '2024-08-01', '2025-02-01', 'Operational'),
('Free Weight Set', 'Strength', '2023-01-25', '2024-07-01', '2025-01-01', 'Operational');

-- Insert Fitness Classes
INSERT INTO FitnessClass (class_name, description, trainer_id, room_id, class_date, start_time, end_time, max_participants, current_participants) VALUES
('Morning Yoga', 'Start your day with energizing yoga flow', 2, 1, '2024-10-25', '07:00:00', '08:00:00', 30, 0),
('HIIT Training', 'High-intensity interval training for maximum results', 3, 3, '2024-10-25', '18:00:00', '19:00:00', 25, 0),
('Strength & Conditioning', 'Build muscle and improve overall strength', 1, 2, '2024-10-26', '10:00:00', '11:30:00', 20, 0),
('Spin Class', 'Indoor cycling for cardio fitness', 3, 4, '2024-10-26', '17:00:00', '18:00:00', 20, 0),
('Evening Yoga', 'Relaxing yoga to unwind after work', 2, 1, '2024-10-27', '18:30:00', '19:30:00', 30, 0);

-- Insert Class Registrations
INSERT INTO ClassRegistration (member_id, class_id, status) VALUES
(1, 3, 'Registered'),
(1, 2, 'Registered'),
(2, 1, 'Registered'),
(3, 4, 'Registered'),
(4, 2, 'Registered'),
(5, 1, 'Registered');

-- Update current participants count
UPDATE FitnessClass SET current_participants = 1 WHERE class_id = 3;
UPDATE FitnessClass SET current_participants = 2 WHERE class_id = 2;
UPDATE FitnessClass SET current_participants = 2 WHERE class_id = 1;
UPDATE FitnessClass SET current_participants = 1 WHERE class_id = 4;

-- Insert Personal Training Sessions
INSERT INTO PersonalTrainingSession (member_id, trainer_id, session_date, start_time, end_time, status, notes) VALUES
(1, 1, '2024-10-25', '14:00:00', '15:00:00', 'Scheduled', 'Focus on upper body strength'),
(2, 2, '2024-10-26', '15:00:00', '16:00:00', 'Scheduled', 'Yoga for flexibility and stress relief'),
(4, 3, '2024-10-27', '09:00:00', '10:00:00', 'Scheduled', 'Cardio endurance training'),
(5, 1, '2024-10-28', '11:00:00', '12:00:00', 'Scheduled', 'Full body workout');

-- Insert Billing Records
INSERT INTO Billing (member_id, billing_date, amount, description, payment_status) VALUES
(1, '2024-10-01', 99.99, 'Monthly Premium Membership Fee', 'Paid'),
(2, '2024-10-01', 149.99, 'Monthly VIP Membership Fee', 'Paid'),
(3, '2024-10-01', 49.99, 'Monthly Basic Membership Fee', 'Paid'),
(4, '2024-10-01', 99.99, 'Monthly Premium Membership Fee', 'Paid'),
(5, '2024-10-01', 149.99, 'Monthly VIP Membership Fee', 'Paid'),
(1, '2024-10-15', 75.00, 'Personal Training Session', 'Pending');
