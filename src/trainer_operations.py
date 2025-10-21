"""
Trainer operations module for Health and Fitness Club Management System
Handles all trainer-related database operations
"""


class TrainerOperations:
    """Manages trainer-related database operations"""
    
    def __init__(self, db_manager):
        """Initialize with a DatabaseManager instance"""
        self.db = db_manager
    
    def add_trainer(self, first_name, last_name, email, phone, date_of_birth,
                    specialization, certification, hourly_rate, available_schedule=None):
        """
        Add a new trainer to the system
        
        Args:
            first_name: Trainer's first name
            last_name: Trainer's last name
            email: Trainer's email
            phone: Trainer's phone number
            date_of_birth: Trainer's date of birth
            specialization: Trainer's area of specialization
            certification: Trainer's certifications
            hourly_rate: Trainer's hourly rate
            available_schedule: JSON object with availability schedule
            
        Returns:
            trainer_id of the newly created trainer
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
            
            # Then, insert into Trainer table
            trainer_query = """
                INSERT INTO Trainer (person_id, specialization, certification, 
                                   hourly_rate, available_schedule)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING trainer_id;
            """
            trainer_params = (person_id, specialization, certification, 
                            hourly_rate, available_schedule)
            trainer_result = self.db.execute_query(trainer_query, trainer_params)
            trainer_id = trainer_result[0]['trainer_id']
            
            print(f"Trainer added successfully with ID: {trainer_id}")
            return trainer_id
            
        except Exception as e:
            print(f"Error adding trainer: {e}")
            raise
    
    def get_trainer_by_id(self, trainer_id):
        """
        Get trainer details by trainer ID
        
        Args:
            trainer_id: Trainer's ID
            
        Returns:
            Trainer details as a dictionary
        """
        query = "SELECT * FROM TrainerDetails WHERE trainer_id = %s;"
        result = self.db.execute_query(query, (trainer_id,))
        return result[0] if result else None
    
    def get_all_trainers(self):
        """
        Get all trainers
        
        Returns:
            List of all trainers
        """
        query = "SELECT * FROM TrainerDetails ORDER BY trainer_id;"
        return self.db.execute_query(query)
    
    def update_trainer_profile(self, trainer_id, **kwargs):
        """
        Update trainer profile information
        
        Args:
            trainer_id: Trainer's ID
            **kwargs: Fields to update
        """
        try:
            person_fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']
            trainer_fields = ['specialization', 'certification', 'hourly_rate', 'available_schedule']
            
            person_updates = {k: v for k, v in kwargs.items() if k in person_fields}
            trainer_updates = {k: v for k, v in kwargs.items() if k in trainer_fields}
            
            # Update Person table if needed
            if person_updates:
                get_person_query = "SELECT person_id FROM Trainer WHERE trainer_id = %s;"
                person_result = self.db.execute_query(get_person_query, (trainer_id,))
                if not person_result:
                    raise ValueError(f"Trainer with ID {trainer_id} not found")
                person_id = person_result[0]['person_id']
                
                set_clause = ', '.join([f"{k} = %s" for k in person_updates.keys()])
                person_query = f"UPDATE Person SET {set_clause} WHERE person_id = %s;"
                person_params = tuple(person_updates.values()) + (person_id,)
                self.db.execute_query(person_query, person_params, fetch=False)
            
            # Update Trainer table if needed
            if trainer_updates:
                set_clause = ', '.join([f"{k} = %s" for k in trainer_updates.keys()])
                trainer_query = f"UPDATE Trainer SET {set_clause} WHERE trainer_id = %s;"
                trainer_params = tuple(trainer_updates.values()) + (trainer_id,)
                self.db.execute_query(trainer_query, trainer_params, fetch=False)
            
            print(f"Trainer {trainer_id} updated successfully")
            
        except Exception as e:
            print(f"Error updating trainer: {e}")
            raise
    
    def get_trainer_schedule(self, trainer_id):
        """
        Get a trainer's schedule
        
        Args:
            trainer_id: Trainer's ID
            
        Returns:
            List of scheduled classes and sessions
        """
        query = """
            SELECT class_name, class_date, start_time, end_time, 
                   room_name, current_participants
            FROM TrainerSchedule
            WHERE trainer_name = (
                SELECT first_name || ' ' || last_name 
                FROM TrainerDetails 
                WHERE trainer_id = %s
            )
            ORDER BY class_date, start_time;
        """
        return self.db.execute_query(query, (trainer_id,))
    
    def get_trainer_personal_sessions(self, trainer_id):
        """
        Get a trainer's personal training sessions
        
        Args:
            trainer_id: Trainer's ID
            
        Returns:
            List of personal training sessions
        """
        query = """
            SELECT pts.session_id, pm.first_name || ' ' || pm.last_name AS member_name,
                   pts.session_date, pts.start_time, pts.end_time, 
                   pts.status, pts.notes
            FROM PersonalTrainingSession pts
            JOIN Member m ON pts.member_id = m.member_id
            JOIN Person pm ON m.person_id = pm.person_id
            WHERE pts.trainer_id = %s AND pts.session_date >= CURRENT_DATE
            ORDER BY pts.session_date, pts.start_time;
        """
        return self.db.execute_query(query, (trainer_id,))
    
    def add_class(self, class_name, description, trainer_id, room_id, 
                  class_date, start_time, end_time, max_participants=20):
        """
        Add a new fitness class
        
        Args:
            class_name: Name of the class
            description: Class description
            trainer_id: Trainer's ID
            room_id: Room ID
            class_date: Date of the class
            start_time: Start time
            end_time: End time
            max_participants: Maximum number of participants
            
        Returns:
            class_id of the newly created class
        """
        try:
            query = """
                INSERT INTO FitnessClass (class_name, description, trainer_id, room_id,
                                        class_date, start_time, end_time, max_participants)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING class_id;
            """
            params = (class_name, description, trainer_id, room_id, 
                     class_date, start_time, end_time, max_participants)
            result = self.db.execute_query(query, params)
            class_id = result[0]['class_id']
            
            print(f"Class added successfully with ID: {class_id}")
            return class_id
            
        except Exception as e:
            print(f"Error adding class: {e}")
            raise
    
    def schedule_personal_session(self, member_id, trainer_id, session_date, 
                                  start_time, end_time, notes=None):
        """
        Schedule a personal training session
        
        Args:
            member_id: Member's ID
            trainer_id: Trainer's ID
            session_date: Date of session
            start_time: Start time
            end_time: End time
            notes: Session notes
            
        Returns:
            session_id
        """
        try:
            query = """
                INSERT INTO PersonalTrainingSession 
                (member_id, trainer_id, session_date, start_time, end_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING session_id;
            """
            params = (member_id, trainer_id, session_date, start_time, end_time, notes)
            result = self.db.execute_query(query, params)
            session_id = result[0]['session_id']
            
            print(f"Personal training session scheduled with ID: {session_id}")
            return session_id
            
        except Exception as e:
            print(f"Error scheduling session: {e}")
            raise
    
    def update_session_status(self, session_id, status, notes=None):
        """
        Update personal training session status
        
        Args:
            session_id: Session ID
            status: New status (Scheduled, Completed, Cancelled)
            notes: Updated notes
        """
        try:
            if notes:
                query = """
                    UPDATE PersonalTrainingSession 
                    SET status = %s, notes = %s 
                    WHERE session_id = %s;
                """
                params = (status, notes, session_id)
            else:
                query = """
                    UPDATE PersonalTrainingSession 
                    SET status = %s 
                    WHERE session_id = %s;
                """
                params = (status, session_id)
            
            self.db.execute_query(query, params, fetch=False)
            print(f"Session {session_id} updated to status: {status}")
            
        except Exception as e:
            print(f"Error updating session: {e}")
            raise
