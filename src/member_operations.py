"""
Member operations module for Health and Fitness Club Management System
Handles all member-related database operations
"""

from datetime import datetime, date


class MemberOperations:
    """Manages member-related database operations"""
    
    def __init__(self, db_manager):
        """Initialize with a DatabaseManager instance"""
        self.db = db_manager
    
    def add_member(self, first_name, last_name, email, phone, date_of_birth, 
                   membership_type, membership_start_date, fitness_goals=None):
        """
        Add a new member to the system
        
        Args:
            first_name: Member's first name
            last_name: Member's last name
            email: Member's email
            phone: Member's phone number
            date_of_birth: Member's date of birth
            membership_type: Type of membership (Basic, Premium, VIP)
            membership_start_date: Start date of membership
            fitness_goals: Member's fitness goals
            
        Returns:
            member_id of the newly created member
        """
        try:
            # First, insert into Person table
            person_query = """
                INSERT INTO Person (first_name, last_name, email, phone, date_of_birth)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING person_id;
            """
            person_params = (first_name, last_name, email, phone, date_of_birth)
            person_result = self.db.execute_query(person_query, person_params)
            person_id = person_result[0]['person_id']
            
            # Then, insert into Member table
            member_query = """
                INSERT INTO Member (person_id, membership_type, membership_start_date, fitness_goals)
                VALUES (%s, %s, %s, %s)
                RETURNING member_id;
            """
            member_params = (person_id, membership_type, membership_start_date, fitness_goals)
            member_result = self.db.execute_query(member_query, member_params)
            member_id = member_result[0]['member_id']
            
            print(f"Member added successfully with ID: {member_id}")
            return member_id
            
        except Exception as e:
            print(f"Error adding member: {e}")
            raise
    
    def get_member_by_id(self, member_id):
        """
        Get member details by member ID
        
        Args:
            member_id: Member's ID
            
        Returns:
            Member details as a dictionary
        """
        query = "SELECT * FROM MemberDetails WHERE member_id = %s;"
        result = self.db.execute_query(query, (member_id,))
        return result[0] if result else None
    
    def get_all_members(self):
        """
        Get all members
        
        Returns:
            List of all members
        """
        query = "SELECT * FROM MemberDetails ORDER BY member_id;"
        return self.db.execute_query(query)
    
    def update_member_profile(self, member_id, **kwargs):
        """
        Update member profile information
        
        Args:
            member_id: Member's ID
            **kwargs: Fields to update (email, phone, fitness_goals, etc.)
        """
        try:
            # Separate Person and Member table updates
            person_fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']
            member_fields = ['membership_type', 'fitness_goals', 'health_metrics']
            
            person_updates = {k: v for k, v in kwargs.items() if k in person_fields}
            member_updates = {k: v for k, v in kwargs.items() if k in member_fields}
            
            # Update Person table if needed
            if person_updates:
                # Get person_id first
                get_person_query = "SELECT person_id FROM Member WHERE member_id = %s;"
                person_result = self.db.execute_query(get_person_query, (member_id,))
                if not person_result:
                    raise ValueError(f"Member with ID {member_id} not found")
                person_id = person_result[0]['person_id']
                
                # Build update query
                set_clause = ', '.join([f"{k} = %s" for k in person_updates.keys()])
                person_query = f"UPDATE Person SET {set_clause} WHERE person_id = %s;"
                person_params = tuple(person_updates.values()) + (person_id,)
                self.db.execute_query(person_query, person_params, fetch=False)
            
            # Update Member table if needed
            if member_updates:
                set_clause = ', '.join([f"{k} = %s" for k in member_updates.keys()])
                member_query = f"UPDATE Member SET {set_clause} WHERE member_id = %s;"
                member_params = tuple(member_updates.values()) + (member_id,)
                self.db.execute_query(member_query, member_params, fetch=False)
            
            print(f"Member {member_id} updated successfully")
            
        except Exception as e:
            print(f"Error updating member: {e}")
            raise
    
    def register_for_class(self, member_id, class_id):
        """
        Register a member for a fitness class
        
        Args:
            member_id: Member's ID
            class_id: Class ID
            
        Returns:
            registration_id
        """
        try:
            # Check if class is full
            check_query = """
                SELECT max_participants, current_participants 
                FROM FitnessClass 
                WHERE class_id = %s;
            """
            result = self.db.execute_query(check_query, (class_id,))
            if not result:
                raise ValueError(f"Class with ID {class_id} not found")
            
            class_info = result[0]
            if class_info['current_participants'] >= class_info['max_participants']:
                raise ValueError("Class is full")
            
            # Register for class
            register_query = """
                INSERT INTO ClassRegistration (member_id, class_id)
                VALUES (%s, %s)
                RETURNING registration_id;
            """
            registration_result = self.db.execute_query(register_query, (member_id, class_id))
            registration_id = registration_result[0]['registration_id']
            
            # Update current participants
            update_query = """
                UPDATE FitnessClass 
                SET current_participants = current_participants + 1 
                WHERE class_id = %s;
            """
            self.db.execute_query(update_query, (class_id,), fetch=False)
            
            print(f"Member {member_id} registered for class {class_id}")
            return registration_id
            
        except Exception as e:
            print(f"Error registering for class: {e}")
            raise
    
    def cancel_class_registration(self, member_id, class_id):
        """
        Cancel a class registration
        
        Args:
            member_id: Member's ID
            class_id: Class ID
        """
        try:
            # Update registration status
            update_query = """
                UPDATE ClassRegistration 
                SET status = 'Cancelled' 
                WHERE member_id = %s AND class_id = %s;
            """
            self.db.execute_query(update_query, (member_id, class_id), fetch=False)
            
            # Update current participants
            update_class_query = """
                UPDATE FitnessClass 
                SET current_participants = current_participants - 1 
                WHERE class_id = %s AND current_participants > 0;
            """
            self.db.execute_query(update_class_query, (class_id,), fetch=False)
            
            print(f"Registration cancelled for member {member_id} and class {class_id}")
            
        except Exception as e:
            print(f"Error cancelling registration: {e}")
            raise
    
    def get_member_schedule(self, member_id):
        """
        Get a member's class schedule
        
        Args:
            member_id: Member's ID
            
        Returns:
            List of scheduled classes
        """
        query = """
            SELECT fc.class_name, fc.class_date, fc.start_time, fc.end_time, 
                   r.room_name, cr.status
            FROM ClassRegistration cr
            JOIN FitnessClass fc ON cr.class_id = fc.class_id
            LEFT JOIN Room r ON fc.room_id = r.room_id
            WHERE cr.member_id = %s AND fc.class_date >= CURRENT_DATE
            ORDER BY fc.class_date, fc.start_time;
        """
        return self.db.execute_query(query, (member_id,))
    
    def get_member_billing_history(self, member_id):
        """
        Get a member's billing history
        
        Args:
            member_id: Member's ID
            
        Returns:
            List of billing records
        """
        query = """
            SELECT billing_id, billing_date, amount, description, 
                   payment_status, payment_date
            FROM Billing
            WHERE member_id = %s
            ORDER BY billing_date DESC;
        """
        return self.db.execute_query(query, (member_id,))
