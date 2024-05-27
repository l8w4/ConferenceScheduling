Certainly! Here is a sample README file for your project, "Optimization-Based Conference Scheduling System":

---

# Optimization-Based Conference Scheduling System

## Introduction

The Optimization-Based Conference Scheduling System is designed to streamline the process of organizing conference schedules. Using optimization techniques, this system assigns attendees to timeslots in a way that maximizes the similarity of their conference abstracts. This ensures that participants with similar research interests are grouped together, enhancing the quality of interactions and discussions during the conference.

## Features

- **User Registration and Login**: Users can register and log in with their roles.
- **Attendee Management**: Add and manage attendees, including their conference titles and abstracts.
- **Schedule Optimization**: Automatically optimizes the conference schedule to maximize the similarity of attendees' abstracts within each timeslot.
- **Similarity Score Calculation**: Calculates similarity scores based on the content of abstracts.
- **Database Integration**: Stores user information, attendee details, similarity scores, and optimized schedules in a MySQL database.
- **Web Interface**: Provides a user-friendly web interface for interaction.

## Technologies Used

- **Python**: Core programming language.
- **Flask**: Web framework for building the web application.
- **MySQL**: Database for storing user and conference data.
- **Gurobi**: Optimization solver for scheduling.
- **HTML/CSS**: Frontend design for web pages.

## Installation

1. **Clone the Repository**
    ```sh
    git clone https://github.com/l8w4/ConferenceScheduling.git
    cd ConferenceScheduling/tree/main/frontAndBackendCodes
    ```

2. **Create a Virtual Environment**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4. **Setup MySQL Database**
    - Ensure MySQL is installed and running.
    - Create a database named `conference_scheduling`.
    - Update `db_config` in `app.py` with your MySQL credentials.

5. **Initialize the Database**
    ```sh
    python initialize_db.py
    ```

6. **Run the Application**
    ```sh
    flask run
    ```

7. **Access the Application**
    - Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage

- **Register**: Create a new user account with a specific role (admin or attendee).
- **Login**: Access the system using your credentials.
- **Admin Panel**: Add and manage attendees, view and optimize the schedule.
- **Attendee Panel**: View your assigned timeslot.

## File Structure

```
frontAndBackendCodes/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│   ├── attendee.html
│   ├── calenderview.html
│   └── ...
│
├── static/
│   ├── css/
│   └── js/
│
├── app.py
├── initialize_db.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

