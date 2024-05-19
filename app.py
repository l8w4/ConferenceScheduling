from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="please",
    password="12345678",
    database="conference_scheduling"
)
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
            return redirect(url_for('admin')) if role == "1" else redirect(url_for('attendee'))
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
        time_slot_id = request.form['time']
        capacity = request.form['chairs']

        cursor.execute("""
            INSERT INTO conferences (conf_title, session_number, day, duration, time_slot, capacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (conf_title, session_number, day, duration, time_slot_id, capacity))
        db.commit()

        return redirect(url_for('admin'))

    cursor.execute("SELECT * FROM conferences")
    conferences = cursor.fetchall()

    cursor.execute("SELECT * FROM timeslots")  # Assuming you have a timeslots table
    timeslots = cursor.fetchall()

    return render_template('admin.html', conferences=conferences, timeslots=timeslots)

@app.route('/calenderview')
def calendar_view():
    cursor.execute("SELECT conf_title, day, start_time, end_time FROM conferences")
    events = cursor.fetchall()
    return render_template('calenderview.html', events=events)


@app.route('/attendee', methods=['GET', 'POST'])
def attendee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        event_id = request.form['event']
        title = request.form['title']
        abstract = request.form['abstract']

        cursor.execute("""
            INSERT INTO attendees (name, email, conf_title, title, abstract)
            VALUES (%s, %s, (SELECT conf_title FROM conferences WHERE id=%s), %s, %s)
        """, (name, email, event_id, title, abstract))
        db.commit()

        return redirect(url_for('attendee'))

    cursor.execute("SELECT id, conf_title FROM conferences")
    events = cursor.fetchall()

    return render_template('attendee.html', events=events)

if __name__ == "_main_":
    app.secret_key = 'your_secret_key'
    app.run(debug=True)