from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields,  ValidationError
import mysql.connector
from mysql.connector import Error

# Connecting to flask app
app = Flask(__name__)
ma = Marshmallow(app)

# Set up for schema of members table
class MembersSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    
    class Meta:
        fields = ("name", "id", "age")

customer_schema = MembersSchema()
customers_schema = MembersSchema(many=True)

# Set up for schema of sessions table
class WorkoutSessionsSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

workout_schema = WorkoutSessionsSchema()
workouts_schema = WorkoutSessionsSchema(many=True)

# Set up for database
def get_db_connection():
    db_name = "members_db"
    user = "root"
    password = "@Deblin312145"
    host = "localhost"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password= password,
            host= host
        )

        print("Connected to MySQL database successfully.")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Shows all members in the members table
@app.route('/', methods=['GET'])
def home():
    # Logic to show all members
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM members"


        cursor.execute(query)
        all_members = cursor.fetchall()

        return customers_schema.jsonify(all_members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Adds a member to the database
@app.route('/members', methods=['POST'])
def add_member():
    # Logic to add a member
    try:
        member_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f'Error: {e}')
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error:": "Database connection failed"})
        cursor = conn.cursor(dictionary=True)

        new_customer = (member_data['id'], member_data['name'], member_data['age'])

        query = "INSERT INTO members (id, name, age) VALUES (%s, %s, %s)"

        cursor.execute(query, new_customer)
        conn.commit()

        return jsonify({"message": "New member added succesfully"}), 201
        
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Gets all the info of the client at a specific ID
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    # Logic to retrieve a member
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members WHERE id = %s"

        cursor.execute(query, (id,))

        members = cursor.fetchall()

        return customers_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Updates a member at a specifi ID
@app.route('/members/update/<int:id>', methods=['PUT'])
def update_member(id):
    # Logic to update a member
        try:
            member_data = customer_schema.load(request.json)
        except ValidationError as e:
            print(f'Error: {e}')
            return jsonify(e.messages), 400
        
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({"error:": "Database connection failed"})
            cursor = conn.cursor(dictionary=True)

            updated_customer = (member_data['name'], member_data['age'], id)

            query = "UPDATE members SET name = %s, age = %s WHERE id = %s"

            cursor.execute(query, updated_customer)
            conn.commit()

            return jsonify({"message": "Member update added succesfully"}), 201
            
        except Error as e:
            print(f"Error: {e}")
            return jsonify({"error": "Internal Server Error"}), 500
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

# Deletes a member at a specified ID
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error:": "Database connection failed"})
        cursor = conn.cursor(dictionary=True)

        member_to_remove = (id,)

        cursor.execute("SELECT * FROM members WHERE id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Customer not found"}), 404
        
        query = "DELETE FROM members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member has been deleted successfully"}), 200
        
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Gets all the workout sessions
@app.route('/workout_sessions', methods=['GET'])
def get_all_sessions():
    # Logic to show all members
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workoutsessions"


        cursor.execute(query)
        all_sessions = cursor.fetchall()

        return workouts_schema.jsonify(all_sessions)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Adds a new workout session
@app.route('/new_session', methods=['POST'])
def add_session():
    # Logic to add a session
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f'Error: {e}')
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        # Check if the member exists
        member_id = workout_data['member_id']
        cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
        member = cursor.fetchone()

        if not member:
            return jsonify({"error": "Member not found"}), 404

        # Prepare data for insertion
        new_session = (member_id, workout_data['session_date'], workout_data['session_time'], workout_data['activity'])
        query = "INSERT INTO workoutsessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"
        
        cursor.execute(query, new_session)
        conn.commit()

        return jsonify({"message": "New session added successfully"}), 201
        
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Updates a workout session at a specified session ID
@app.route('/sessions/update/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    # Logic to update a session
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f'Validation Error: {e.messages}')  # More informative error message
        return jsonify({"error": e.messages}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)

        updated_session = (workout_data['member_id'], workout_data['session_date'], workout_data['session_time'], workout_data['activity'], session_id)

        query = "UPDATE workoutsessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"
        
        # Execute the query and check how many rows were affected
        cursor.execute(query, updated_session)

        conn.commit()

        return jsonify({"message": "Session updated successfully"}), 200
        
    except Error as e:
        print(f"Database Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Gets all workout sessions of a specified member ID
@app.route('/sessions/<int:member_id>', methods=['GET'])
def get_member_sessions(member_id):
    # Logic to retrieve a member
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workoutsessions WHERE member_id = %s"

        cursor.execute(query, (member_id,))

        members = cursor.fetchall()

        return workouts_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)