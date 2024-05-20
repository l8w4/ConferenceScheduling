from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'please'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'database': os.getenv('DB_NAME', 'conference_scheduling')
}

db = mysql.connector.connect(**db_config)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

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

# In your Flask app.py file

from flask import Flask, render_template, request

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        conf_title = request.form['Title']
        session_number = request.form['Session']
        day = request.form['day']
        duration = request.form['duration']
        capacity = request.form['chairs']
        
        # Insert data into conferences table
        cursor.execute("INSERT INTO conferences (conf_title, session_number, day, duration, capacity) VALUES (%s, %s, %s, %s, %s)", (conf_title, session_number, day, duration, capacity))
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

    return render_template('attendee.html',conferences=conferences)

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

@app.route('/api/events')
def get_events():
    cursor.execute("SELECT id, conf_title, session_number, day, duration, capacity FROM conferences")
    conferences = cursor.fetchall()
    events = []
    for conf in conferences:
        start_date = conf[3]
        end_date = start_date + timedelta(days=conf[4])  # Duration is inclusive of the start date
        event = {
            'title': conf[1],
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),  # End date is exclusive
            'extendedProps': {
                'capacity': conf[5],
                'room': conf[2]
            }
        }
        events.append(event)
    return jsonify(events)




if __name__ == "__main__":
    app.run(debug=True)
