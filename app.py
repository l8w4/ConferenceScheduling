from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from datetime import timedelta, datetime
import os
import gurobipy as gp
from gurobipy import GRB
from gurobipy import *


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'please'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'database': os.getenv('DB_NAME', 'conference_scheduling')
}

# Connect to the database
db = mysql.connector.connect(**db_config)
cursor = db.cursor()


def fetch_data_from_database():
    cursor.execute("SELECT id, conf_title, session_number, duration, capacity FROM conferences")
    conferences = cursor.fetchall()

    cursor.execute("SELECT abstract1_id, abstract2_id, similarity_score FROM similarity_scores")
    similarity_scores = cursor.fetchall()

    cursor.execute("SELECT id, start_time, end_time FROM timeslots")
    timeslots = cursor.fetchall()

    cursor.execute("SELECT id, name, email, conf_title, title, abstract, start_time, end_time FROM attendees")
    attendees = cursor.fetchall()

    # Convert attendees tuple to list of lists
    attendees = [list(row) for row in attendees]

    return conferences, similarity_scores, timeslots, attendees

def fetch_speakers_data_from_database(event_id):
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="please",
        password="12345678",
        database="conference_scheduling"
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Define the SQL query to fetch speakers' data for the given event_id
    query = "SELECT name FROM attendees WHERE conf_title = %s"
    params = (event_id,)

    # Execute the query
    cursor.execute(query, params)

    # Fetch all the rows returned by the query
    speakers_data = cursor.fetchall()

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    # Transform the fetched data into a list of dictionaries
    speakers = []
    for speaker in speakers_data:
        speakers.append({
            'name': speaker[0],
            'start_time': None,  # Assign None for now, to be determined by the optimization engine
            'end_time': None  # Assign None for now, to be determined by the optimization engine
        })

    return speakers

@app.route('/')
def index():
    return render_template('index.html')

def calculate_similarity_score(abstract1, abstract2): #Jaccard Similarity
    abstract1 = str(abstract1)
    abstract2 = str(abstract2)
    words1 = set(abstract1.split())
    words2 = set(abstract2.split())
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    similarity_score = intersection / union if union != 0 else 0  # Avoid division by zero
    return similarity_score

def store_similarity_scores(conferences, cursor):
    for i in range(len(conferences)):
        for j in range(i + 1, len(conferences)):
            abstract1 = conferences[i][2]  # Assuming abstract is at index 2
            abstract2 = conferences[j][2]
            score = calculate_similarity_score(abstract1, abstract2)
            abstract1_id = conferences[i][0]
            abstract2_id = conferences[j][0]
            cursor.execute(
                "INSERT INTO similarity_scores (abstract1_id, abstract2_id, similarity_score) VALUES (%s, %s, %s)",
                (abstract1_id, abstract2_id, score)
            )
def fetch_conference_details():
    cursor.execute("SELECT num_sessions FROM conference_details LIMIT 1")
    result = cursor.fetchone()
    if result:
        return {'num_sessions': result[0]}
    else:
        return {'num_sessions': 1}  # Default to 1 session if no details are found

def main():
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="please",
        password="12345678",
        database="conference_scheduling"
    )

    # Create cursor object
    cursor = connection.cursor()

    # Execute query to retrieve abstracts
    cursor.execute("SELECT id, conf_title, abstract FROM attendees")

    # Fetch all abstracts
    abstracts = cursor.fetchall()

    # Calculate similarity scores for each pair of abstracts
    similarity_scores = []
    for i in range(len(abstracts)):
        for j in range(i+1, len(abstracts)):
            abstract1 = abstracts[i][2]
            abstract2 = abstracts[j][2]
            similarity_score = calculate_similarity_score(abstract1, abstract2)
            abstract1_id = abstracts[i][0]
            abstract2_id = abstracts[j][0]
            similarity_scores.append((abstract1_id, abstract2_id, similarity_score))
            print(f"Similarity score between Abstract {abstract1_id} and Abstract {abstract2_id}: {similarity_score}")

    # Store similarity scores in the database
    for score in similarity_scores:
        cursor.execute(
            "INSERT INTO similarity_scores (abstract1_id, abstract2_id, similarity_score) VALUES (%s, %s, %s)",
            score
        )

    # Commit changes to the database
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

    # Fetch data from the database
    #conferences, similarity_scores, timeslots = fetch_data_from_database()

    # Process and use the data as needed
    optimize_schedule()
    get_events()

@app.route('/optimize_schedule')
def optimize_schedule():
    conferences, similarity_scores, timeslots, attendees = fetch_data_from_database()

    num_days = 2  # Maximum 2 days for conferences
    num_time_slots = len(timeslots)  # Number of time slots fetched from the database

    # Define time constants
    start_time_10am = datetime.strptime('10:00:00', '%H:%M:%S')
    end_time_5pm = datetime.strptime('17:00:00', '%H:%M:%S')

    # Define the time increment
    time_increment = timedelta(hours=1)

    schedule = {}
    connection = mysql.connector.connect(
        host='localhost',
        user='please',
        password='12345678',
        database='conference_scheduling'
    )
    cursor = connection.cursor()

    current_time = start_time_10am  # Initialize current time

    for j in range(num_days):
        for k in range(num_time_slots):
            schedule[(j, k)] = []

            for attendee in attendees:
                attendee_id, name, email, conf_title, title, abstract, _, _ = attendee

                # Fetch the conference session number for the current attendee
                cursor.execute("SELECT session_number FROM conferences WHERE conf_title = %s", (conf_title,))
                attendee_session_number = cursor.fetchone()[0]

                # Check if the current attendee belongs to the current conference and session
                if conf_title == attendee[3] and attendee_session_number == attendee[2]:
                    # Assign time slots to the attendee
                    start_time = current_time.strftime('%H:%M:%S')
                    end_time = (current_time + time_increment).strftime('%H:%M:%S')

                    # Ensure end_time doesn't exceed 5 PM
                    if current_time + time_increment > end_time_5pm:
                        end_time = end_time_5pm.strftime('%H:%M:%S')

                    # Update the database with the assigned time slots
                    cursor.execute("""
                        UPDATE attendees
                        SET start_time = %s, end_time = %s
                        WHERE id = %s
                    """, (start_time, end_time, attendee_id))
                    connection.commit()

                    # Update the schedule dictionary
                    schedule[(j, k)].append((name, f"Start Time: {start_time}, End Time: {end_time}"))

                    # Move to the next time slot
                    current_time += time_increment

                    # Break if the next time slot exceeds 5 PM
                    if current_time >= end_time_5pm:
                        break

        # Reset current time to 10 AM for the next day
        current_time = start_time_10am

    connection.close()

    # Render the optimized schedule template with the schedule data
    with app.app_context():
        return render_template('calenderview.html', schedule=schedule)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        db.commit()
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role=%s", (username, password, role))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            session['role'] = role
            if role == "1":
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('attendee'))
        else:
            return render_template('login.html', status=0)

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        conf_title = request.form['Title']
        session_number = request.form['Session']
        day = request.form['day']
        duration = request.form['duration']
        capacity = request.form['chairs']

        # Insert data into conferences table
        cursor.execute(
            "INSERT INTO conferences (conf_title, session_number, day, duration, capacity) VALUES (%s, %s, %s, %s, %s)",
            (conf_title, session_number, day, duration, capacity))
        db.commit()  # Commit the transaction

        # Redirect to admin route to refresh the page
        return redirect(url_for('admin'))

    # Fetch conferences data from the database
    cursor.execute("SELECT id, conf_title, session_number, day, duration, capacity FROM conferences")
    conferences = cursor.fetchall()
    return render_template('admin.html', conferences=conferences)

@app.route('/attendee', methods=['GET', 'POST'])
def attendee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        event_id = request.form['event']
        title_p = request.form['title_p']
        abstract = request.form['abstract']

        cursor.execute("""
            INSERT INTO attendees (name, email, conf_title, title, abstract)
            VALUES (%s, %s,%s, %s, %s)
        """, (name, email, event_id, title_p, abstract))
        db.commit()

        return redirect(url_for('attendee'))
    cursor.execute("SELECT id, conf_title, session_number, day, duration, capacity FROM conferences")
    conferences = cursor.fetchall()

    return render_template('attendee.html', conferences=conferences)


@app.route('/delete_conference/<int:conference_id>', methods=['POST'])
def delete_conference(conference_id):
    cursor.execute("DELETE FROM conferences WHERE id=%s", (conference_id,))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/edit_conference/<int:conference_id>', methods=['GET', 'POST'])
def edit_conference(conference_id):
    if request.method == 'POST':
        conf_title = request.form['Title']
        session_number = request.form['Session']
        day = request.form['day']
        duration = request.form['duration']
        capacity = request.form['chairs']

        cursor.execute("""
            UPDATE conferences 
            SET conf_title=%s, session_number=%s, day=%s, duration=%s, capacity=%s 
            WHERE id=%s
        """, (conf_title, session_number, day, duration, capacity, conference_id))
        db.commit()

        return redirect(url_for('admin'))

    cursor.execute("SELECT * FROM conferences WHERE id=%s", (conference_id,))
    conference = cursor.fetchone()

    return render_template('edit_conference.html', conference=conference)


@app.route('/calenderview')
def calendar_view():
    return render_template('calenderview.html')

from flask import jsonify

@app.route('/api/events')
def get_events():
    cursor.execute("SELECT id, conf_title, session_number, day, duration, capacity FROM conferences")
    conferences = cursor.fetchall()
    
    # Print out the fetched conferences for debugging
    print("Fetched conferences:", conferences)

    events = []
    for conf in conferences:
        start_date = conf[3]
        end_date = start_date + timedelta(days=conf[4])  # Duration is inclusive
        # Duration is inclusive of the start date
        event = {
            'title': conf[1],
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),  # End date is exclusive
            'duration_days': conf[4],  # Adding duration in days as a separate field
            'extendedProps': {
                'capacity': conf[5],
                'session_number': conf[2],
                'speakers': get_speakers(conf[1])  # Assuming conf[1] is the conf_title
            }
        }
        
        # Convert timedelta objects to strings
        for speaker in event['extendedProps']['speakers']:
            speaker['start_time'] = str(speaker['start_time'])
            speaker['end_time'] = str(speaker['end_time'])
        
        events.append(event)
    
    # Print out the formatted events for debugging
    print("Formatted events:", events)

    with app.app_context():
        return jsonify(events)

def get_speakers(conf_title):
    cursor.execute("SELECT name, start_time, end_time FROM attendees WHERE conf_title = %s", (conf_title,))
    speakers = cursor.fetchall()
    return [{'name': speaker[0], 'start_time': speaker[1], 'end_time': speaker[2]} for speaker in speakers]

def get_start_time(conference_id):
    cursor.execute("SELECT start_time FROM timeslots WHERE id = (SELECT MIN(id) FROM timeslots WHERE conference_id = %s)", (conference_id,))
    start_time = cursor.fetchone()
    return start_time[0] if start_time else None

def get_end_time(conference_id):
    cursor.execute("SELECT end_time FROM timeslots WHERE id = (SELECT MAX(id) FROM timeslots WHERE conference_id = %s)", (conference_id,))
    end_time = cursor.fetchone()
    return end_time[0] if end_time else None

if __name__ == "__main__":
    app.run(debug=True)
main()

