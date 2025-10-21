"""
Admin operations module for Health and Fitness Club Management System
Handles administrative database operations
"""


class AdminOperations:
    """Manages administrative database operations"""
    
    def __init__(self, db_manager):
        """Initialize with a DatabaseManager instance"""
        self.db = db_manager
    
    # Room Management
    def add_room(self, room_name, capacity, equipment_available, status='Available'):
        """
        Add a new room
        
        Args:
            room_name: Name of the room
            capacity: Room capacity
            equipment_available: Description of available equipment
            status: Room status
            
        Returns:
            room_id
        """
        try:
            query = """
                INSERT INTO Room (room_name, capacity, equipment_available, status)
                VALUES (%s, %s, %s, %s)
                RETURNING room_id;
            """
            params = (room_name, capacity, equipment_available, status)
            result = self.db.execute_query(query, params)
            room_id = result[0]['room_id']
            
            print(f"Room added successfully with ID: {room_id}")
            return room_id
            
        except Exception as e:
            print(f"Error adding room: {e}")
            raise
    
    def get_all_rooms(self):
        """Get all rooms"""
        query = "SELECT * FROM Room ORDER BY room_id;"
        return self.db.execute_query(query)
    
    def update_room_status(self, room_id, status):
        """
        Update room status
        
        Args:
            room_id: Room ID
            status: New status (Available, Occupied, Maintenance)
        """
        try:
            query = "UPDATE Room SET status = %s WHERE room_id = %s;"
            self.db.execute_query(query, (status, room_id), fetch=False)
            print(f"Room {room_id} status updated to: {status}")
        except Exception as e:
            print(f"Error updating room status: {e}")
            raise
    
    # Equipment Management
    def add_equipment(self, equipment_name, equipment_type, purchase_date, 
                     next_maintenance_date, status='Operational'):
        """
        Add new equipment
        
        Args:
            equipment_name: Name of equipment
            equipment_type: Type of equipment
            purchase_date: Date of purchase
            next_maintenance_date: Next maintenance date
            status: Equipment status
            
        Returns:
            equipment_id
        """
        try:
            query = """
                INSERT INTO Equipment (equipment_name, equipment_type, purchase_date, 
                                     next_maintenance_date, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING equipment_id;
            """
            params = (equipment_name, equipment_type, purchase_date, 
                     next_maintenance_date, status)
            result = self.db.execute_query(query, params)
            equipment_id = result[0]['equipment_id']
            
            print(f"Equipment added successfully with ID: {equipment_id}")
            return equipment_id
            
        except Exception as e:
            print(f"Error adding equipment: {e}")
            raise
    
    def get_all_equipment(self):
        """Get all equipment"""
        query = "SELECT * FROM Equipment ORDER BY equipment_id;"
        return self.db.execute_query(query)
    
    def get_equipment_maintenance_schedule(self):
        """Get equipment maintenance schedule"""
        query = "SELECT * FROM EquipmentMaintenanceSchedule ORDER BY next_maintenance_date;"
        return self.db.execute_query(query)
    
    def update_equipment_maintenance(self, equipment_id, last_maintenance_date, 
                                    next_maintenance_date):
        """
        Update equipment maintenance dates
        
        Args:
            equipment_id: Equipment ID
            last_maintenance_date: Last maintenance date
            next_maintenance_date: Next maintenance date
        """
        try:
            query = """
                UPDATE Equipment 
                SET last_maintenance_date = %s, next_maintenance_date = %s 
                WHERE equipment_id = %s;
            """
            params = (last_maintenance_date, next_maintenance_date, equipment_id)
            self.db.execute_query(query, params, fetch=False)
            print(f"Equipment {equipment_id} maintenance dates updated")
        except Exception as e:
            print(f"Error updating equipment maintenance: {e}")
            raise
    
    def update_equipment_status(self, equipment_id, status):
        """
        Update equipment status
        
        Args:
            equipment_id: Equipment ID
            status: New status (Operational, Under Maintenance, Out of Service)
        """
        try:
            query = "UPDATE Equipment SET status = %s WHERE equipment_id = %s;"
            self.db.execute_query(query, (status, equipment_id), fetch=False)
            print(f"Equipment {equipment_id} status updated to: {status}")
        except Exception as e:
            print(f"Error updating equipment status: {e}")
            raise
    
    # Class Management
    def get_all_classes(self):
        """Get all fitness classes"""
        query = """
            SELECT fc.*, p.first_name || ' ' || p.last_name AS trainer_name,
                   r.room_name
            FROM FitnessClass fc
            LEFT JOIN Trainer t ON fc.trainer_id = t.trainer_id
            LEFT JOIN Person p ON t.person_id = p.person_id
            LEFT JOIN Room r ON fc.room_id = r.room_id
            ORDER BY fc.class_date, fc.start_time;
        """
        return self.db.execute_query(query)
    
    def get_upcoming_classes(self):
        """Get upcoming fitness classes"""
        query = "SELECT * FROM UpcomingClasses;"
        return self.db.execute_query(query)
    
    def get_class_attendance_stats(self):
        """Get class attendance statistics"""
        query = "SELECT * FROM ClassAttendanceStats ORDER BY class_date DESC;"
        return self.db.execute_query(query)
    
    def update_class_attendance(self, registration_id, status='Attended'):
        """
        Update class attendance status
        
        Args:
            registration_id: Registration ID
            status: New status (Attended, Cancelled, etc.)
        """
        try:
            query = "UPDATE ClassRegistration SET status = %s WHERE registration_id = %s;"
            self.db.execute_query(query, (status, registration_id), fetch=False)
            print(f"Registration {registration_id} updated to: {status}")
        except Exception as e:
            print(f"Error updating attendance: {e}")
            raise
    
    # Billing Management
    def create_billing_record(self, member_id, amount, description, 
                             billing_date=None, payment_status='Pending'):
        """
        Create a billing record
        
        Args:
            member_id: Member ID
            amount: Billing amount
            description: Description of charge
            billing_date: Date of billing
            payment_status: Payment status
            
        Returns:
            billing_id
        """
        try:
            if billing_date:
                query = """
                    INSERT INTO Billing (member_id, billing_date, amount, description, payment_status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING billing_id;
                """
                params = (member_id, billing_date, amount, description, payment_status)
            else:
                query = """
                    INSERT INTO Billing (member_id, amount, description, payment_status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING billing_id;
                """
                params = (member_id, amount, description, payment_status)
            
            result = self.db.execute_query(query, params)
            billing_id = result[0]['billing_id']
            
            print(f"Billing record created with ID: {billing_id}")
            return billing_id
            
        except Exception as e:
            print(f"Error creating billing record: {e}")
            raise
    
    def update_payment_status(self, billing_id, payment_status, payment_date=None):
        """
        Update payment status
        
        Args:
            billing_id: Billing ID
            payment_status: New payment status (Paid, Pending, Overdue)
            payment_date: Date of payment
        """
        try:
            if payment_date:
                query = """
                    UPDATE Billing 
                    SET payment_status = %s, payment_date = %s 
                    WHERE billing_id = %s;
                """
                params = (payment_status, payment_date, billing_id)
            else:
                query = "UPDATE Billing SET payment_status = %s WHERE billing_id = %s;"
                params = (payment_status, billing_id)
            
            self.db.execute_query(query, params, fetch=False)
            print(f"Billing {billing_id} payment status updated to: {payment_status}")
        except Exception as e:
            print(f"Error updating payment status: {e}")
            raise
    
    def get_all_billing_records(self):
        """Get all billing records"""
        query = """
            SELECT b.*, p.first_name || ' ' || p.last_name AS member_name
            FROM Billing b
            JOIN Member m ON b.member_id = m.member_id
            JOIN Person p ON m.person_id = p.person_id
            ORDER BY b.billing_date DESC;
        """
        return self.db.execute_query(query)
    
    def get_member_billing_summary(self):
        """Get billing summary for all members"""
        query = "SELECT * FROM MemberBillingSummary ORDER BY member_id;"
        return self.db.execute_query(query)
    
    # Reports and Analytics
    def get_room_utilization(self):
        """Get room utilization report"""
        query = "SELECT * FROM RoomUtilization;"
        return self.db.execute_query(query)
    
    def get_popular_classes(self):
        """Get popular classes report"""
        query = "SELECT * FROM PopularClasses;"
        return self.db.execute_query(query)
    
    def get_trainer_workload(self):
        """Get trainer workload report"""
        query = """
            SELECT t.trainer_id, p.first_name || ' ' || p.last_name AS trainer_name,
                   COUNT(DISTINCT fc.class_id) AS total_classes,
                   COUNT(DISTINCT pts.session_id) AS total_sessions
            FROM Trainer t
            JOIN Person p ON t.person_id = p.person_id
            LEFT JOIN FitnessClass fc ON t.trainer_id = fc.trainer_id 
                AND fc.class_date >= CURRENT_DATE
            LEFT JOIN PersonalTrainingSession pts ON t.trainer_id = pts.trainer_id 
                AND pts.session_date >= CURRENT_DATE
            GROUP BY t.trainer_id, p.first_name, p.last_name
            ORDER BY total_classes DESC, total_sessions DESC;
        """
        return self.db.execute_query(query)
    
    def get_membership_statistics(self):
        """Get membership statistics"""
        query = """
            SELECT membership_type, COUNT(*) AS member_count
            FROM Member
            WHERE membership_end_date IS NULL OR membership_end_date >= CURRENT_DATE
            GROUP BY membership_type
            ORDER BY member_count DESC;
        """
        return self.db.execute_query(query)
