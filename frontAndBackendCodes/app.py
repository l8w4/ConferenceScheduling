from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from flask import current_app
from datetime import timedelta, datetime
import os
import gurobipy as gp
from gurobipy import GRB, Model
from gurobipy import *
from itertools import cycle

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
    cursor.execute("SELECT id, TIME_FORMAT(start_time, '%H:%i:%s'), TIME_FORMAT(end_time, '%H:%i:%s') FROM timeslots")
    timeslots_data = cursor.fetchall()

    # Convert timeslots data to list of tuples with string times
    timeslots = [(row[0], row[1], row[2]) for row in timeslots_data]

    cursor.execute("SELECT id, name, email, conf_title, title, abstract FROM attendees")
    attendees_data = cursor.fetchall()

    # Convert attendees tuple to list of lists
    attendees = [list(row) for row in attendees_data]

    return timeslots, attendees

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

previous_log_message = None

def log_unique(message):
    global previous_log_message
    if message != previous_log_message:
        print(message)
        previous_log_message = message

def main():
    with app.app_context():
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

from flask import render_template


def optimize_schedule():
    cursor.execute("SELECT conf_title FROM conferences")
    conferences = cursor.fetchall()

    for conference in conferences:
        conference_title = conference[0]

        # Fetch attendees of the conference
        cursor.execute("SELECT id, abstract FROM attendees WHERE conf_title = %s", (conference_title,))
        attendees = cursor.fetchall()

        # Calculate similarity scores between attendees' abstracts
        similarity_scores = []
        for i in range(len(attendees)):
            for j in range(i + 1, len(attendees)):
                abstract1 = attendees[i][1]
                abstract2 = attendees[j][1]
                similarity_score = calculate_similarity_score(abstract1, abstract2)
                attendee1_id = attendees[i][0]
                attendee2_id = attendees[j][0]
                similarity_scores.append((attendee1_id, attendee2_id, similarity_score))

        # Sort similarity scores in descending order
        similarity_scores.sort(key=lambda x: x[2], reverse=True)

        # Assign order to attendees
        order = 1
        assigned_orders = set()
        for score in similarity_scores:
            attendee1_id, attendee2_id, similarity_score = score
            if attendee1_id not in assigned_orders:
                cursor.execute("UPDATE attendees SET optimal_order = %s WHERE id = %s", (order, attendee1_id))
                assigned_orders.add(attendee1_id)
                order += 1
            if attendee2_id not in assigned_orders:
                cursor.execute("UPDATE attendees SET optimal_order = %s WHERE id = %s", (order, attendee2_id))
                assigned_orders.add(attendee2_id)
                order += 1

        # Ensure all attendees have an optimal order
        for attendee in attendees:
            if attendee[0] not in assigned_orders:
                cursor.execute("UPDATE attendees SET optimal_order = %s WHERE id = %s", (order, attendee[0]))
                assigned_orders.add(attendee[0])
                order += 1

        # Fetch timeslots
        cursor.execute("SELECT id, start_time, end_time FROM timeslots")
        timeslots = cursor.fetchall()
        num_timeslots = len(timeslots)

        for attendee in attendees:
            attendee_id = attendee[0]
            cursor.execute("SELECT optimal_order FROM attendees WHERE id = %s", (attendee_id,))
            optimal_order = cursor.fetchone()[0]
            if optimal_order is not None:  # Check if optimal_order is not None
                timeslot_index = (optimal_order - 1) % num_timeslots
                timeslot_id = timeslots[timeslot_index][0]
                cursor.execute("UPDATE attendees SET start_time = %s, end_time = %s WHERE id = %s",
                               (timeslots[timeslot_index][1], timeslots[timeslot_index][2], attendee_id))
            else:
                print(f"Optimal order is None for attendee_id {attendee_id}, skipping timeslot assignment.")

        # Commit changes to the database
        db.commit()

@app.route('/optimize_schedule')
def optimize_schedule_route():
    return optimize_schedule()

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

        # Fetch the number of sessions for the selected conference
        cursor.execute("SELECT session_number FROM conferences WHERE conf_title = %s", (event_id,))
        session_number = cursor.fetchone()

        if session_number is None:
            return render_template('error.html', error_message="Conference not found")

        session_number = session_number[0]

        # Count the number of attendees for the selected conference
        cursor.execute("SELECT COUNT(*) FROM attendees WHERE conf_title = %s", (event_id,))
        attendee_count = cursor.fetchone()[0]

        # Check if the limit is reached based on the number of sessions
        if (session_number == 1 and attendee_count >= 7) or (session_number == 2 and attendee_count >= 14):
            return render_template('error.html', error_message="Registration limit reached for this conference, please select another one.")

        # Insert the new attendee if the limit is not reached
        cursor.execute("""
            INSERT INTO attendees (name, email, conf_title, title, abstract)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, event_id, title_p, abstract))
        db.commit()

        return redirect(url_for('attendee'))

    # Fetch conferences data from the database
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