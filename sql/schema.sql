-- Health and Fitness Club Management System Database Schema
-- COMP3005 Final Project

-- Drop existing tables if they exist (for fresh setup)
DROP TABLE IF EXISTS Billing CASCADE;
DROP TABLE IF EXISTS ClassRegistration CASCADE;
DROP TABLE IF EXISTS PersonalTrainingSession CASCADE;
DROP TABLE IF EXISTS FitnessClass CASCADE;
DROP TABLE IF EXISTS Equipment CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS Trainer CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS AdminStaff CASCADE;
DROP TABLE IF EXISTS Person CASCADE;

-- Person table (base table for all users)
CREATE TABLE Person (
    person_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Member table (fitness club members)
CREATE TABLE Member (
    member_id SERIAL PRIMARY KEY,
    person_id INTEGER UNIQUE NOT NULL,
    membership_type VARCHAR(50) NOT NULL CHECK (membership_type IN ('Basic', 'Premium', 'VIP')),
    membership_start_date DATE NOT NULL,
    membership_end_date DATE,
    health_metrics JSONB, -- Store health data like weight, height, BMI, etc.
    fitness_goals TEXT,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

-- Trainer table (personal trainers)
CREATE TABLE Trainer (
    trainer_id SERIAL PRIMARY KEY,
    person_id INTEGER UNIQUE NOT NULL,
    specialization VARCHAR(100),
    certification VARCHAR(255),
    hourly_rate DECIMAL(10, 2),
    available_schedule JSONB, -- Store availability as JSON
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

-- Admin Staff table
CREATE TABLE AdminStaff (
    admin_id SERIAL PRIMARY KEY,
    person_id INTEGER UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

-- Room table (fitness club rooms)
CREATE TABLE Room (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL,
    equipment_available TEXT,
    status VARCHAR(20) DEFAULT 'Available' CHECK (status IN ('Available', 'Occupied', 'Maintenance'))
);

-- Equipment table
CREATE TABLE Equipment (
    equipment_id SERIAL PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50),
    purchase_date DATE,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    status VARCHAR(20) DEFAULT 'Operational' CHECK (status IN ('Operational', 'Under Maintenance', 'Out of Service'))
);

-- Fitness Class table
CREATE TABLE FitnessClass (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    description TEXT,
    trainer_id INTEGER,
    room_id INTEGER,
    class_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_participants INTEGER DEFAULT 20,
    current_participants INTEGER DEFAULT 0,
    FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id) ON DELETE SET NULL,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE SET NULL
);

-- Class Registration table (Many-to-Many relationship between Members and Classes)
CREATE TABLE ClassRegistration (
    registration_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Registered' CHECK (status IN ('Registered', 'Attended', 'Cancelled')),
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES FitnessClass(class_id) ON DELETE CASCADE,
    UNIQUE(member_id, class_id)
);

-- Personal Training Session table
CREATE TABLE PersonalTrainingSession (
    session_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    trainer_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id) ON DELETE CASCADE
);

-- Billing table
CREATE TABLE Billing (
    billing_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    billing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    payment_status VARCHAR(20) DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Paid', 'Overdue')),
    payment_date DATE,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_member_person ON Member(person_id);
CREATE INDEX idx_trainer_person ON Trainer(person_id);
CREATE INDEX idx_admin_person ON AdminStaff(person_id);
CREATE INDEX idx_class_registration_member ON ClassRegistration(member_id);
CREATE INDEX idx_class_registration_class ON ClassRegistration(class_id);
CREATE INDEX idx_personal_session_member ON PersonalTrainingSession(member_id);
CREATE INDEX idx_personal_session_trainer ON PersonalTrainingSession(trainer_id);
CREATE INDEX idx_billing_member ON Billing(member_id);
CREATE INDEX idx_fitness_class_date ON FitnessClass(class_date);
