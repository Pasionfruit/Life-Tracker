from flask import Flask, render_template, jsonify, request, redirect, session, url_for, make_response, abort
from functools import wraps
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import sqlite3

import calendar
from datetime import datetime, timedelta

app = Flask(__name__)

date_statuses = {
    '2024-12-01': 'green',
    '2024-12-03': 'green',
    '2024-12-15': 'yellow',
    '2024-12-02': 'red',
}
# Load environment variables
load_dotenv()

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('Tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor() 

    habits_table = 'habits'
    goals_table = 'goals'
    subtask_table = 'subtasks'

    drop_habits = f"DROP TABLE IF EXISTS {habits_table}"
    drop_goals = f"DROP TABLE IF EXISTS {goals_table}"
    drop_subtask = f"DROP TABLE IF EXISTS {subtask_table}"

    cursor.execute(drop_habits)
    cursor.execute(drop_goals)
    cursor.execute(drop_subtask)

    # Re-create the habits table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Goal INTEGER NOT NULL,
        Increment INTEGER NOT NULL,
        Unit TEXT NOT NULL,
        Progress INTEGER DEFAULT 0,
        Streak INTEGER DEFAULT 0
    );
    """)

    # Re-create the goal table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        Goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT NOT NULL,
        Created_at TEXT NOT NULL
    );
    """)

    # Re-create the subtask table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subtasks (
        Subtask_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Goal_id INTEGER NOT NULL,
        Name TEXT NOT NULL,
        Priority TEXT NOT NULL,
        Due_date TEXT NOT NULL,
        Description TEXT NOT NULL,
        Status TEXT NOT NULL
        FOREIGN KEY (Goal_id) REFERENCES goals (Goal_id)
    );
    """)

    # Insert data into `habits` only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM habits")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        cursor.executemany("""
        INSERT INTO habits (Name, Goal, Increment, Unit, Progress, Streak)
        VALUES (?, ?, ?, ?, ?, ?)""", [
            ("Drink Water", 8, 1, "Times", 0, 3),
        ])

    conn.commit()
    conn.close()

initialize_db()
    
# Function to get the calendar for a specific month and year
def get_calendar_data(date):
    # Get the first day of the month and total days in the month
    first_day_of_month = date.replace(day=1)
    first_weekday, days_in_month = calendar.monthrange(date.year, date.month)
    
    # Create a list of days to be displayed in the calendar
    days = []
    for day in range(1, days_in_month + 1):
        full_date = date.replace(day=day).strftime('%Y-%m-%d')
        status = date_statuses.get(full_date, None)  # Get status from date_statuses
        days.append({'day': day, 'full_date': full_date, 'status': status})
    
    # Prepare the month and year header
    month_year = date.strftime('%B %Y')
    
    return {
        'month_year': month_year,
        'days': days,
        'first_weekday': first_weekday,
    }

def get_habit_by_id(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
    habit = cursor.fetchone()
    conn.close()
    return habit

# # Habit page
@app.route('/')
@app.route('/Habit.html')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits")
    habits = cursor.fetchall()

    habit_data = []
    for habit in habits:
        habit_data.append({
            'id': habit['id'],
            'Name': habit['Name'],
            'Goal': habit['Goal'],
            'Increment': habit['Increment'],
            'Unit': habit['Unit'],
            'Progress': habit['Progress'],
            'Streak': habit['Streak']
        })

    conn.close()
    return render_template('Habit.html', habits=habit_data)

@app.route('/increment', methods=['POST'])
def increment():
    habit_id = request.json.get('id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
    habit = cursor.fetchone()

    if habit:
        new_progress = habit['Progress'] + habit['Increment']
        cursor.execute(
            "UPDATE habits SET Progress = ? WHERE id = ?", (new_progress, habit_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "Progress": new_progress})
    else:
        conn.close()
        return jsonify({"success": False, "message": "Habit not found"}), 404

@app.route('/Stat.html')
@app.route('/<int:year>/<int:month>')
def schedule(year=None, month=None):
    # Default to the current date if no year or month is provided
    if not year or not month:
        current_date = datetime.today()
    else:
        current_date = datetime(year, month, 1)

    calendar_data = get_calendar_data(current_date)
    
    return render_template('Stat.html', calendar_data=calendar_data, current_date=current_date)

@app.route('/AddHabit.html', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form['name']
        goal = request.form['goal']
        increment = request.form['increment']
        unit = request.form['unit']
        
        errors = []

        if not name:
            errors.append('Name is required')

        try:
            goal = int(goal)
            increment = int(increment)
            if increment <= 0:
                errors.append('Increment must be greater than 0')
        except ValueError:
            errors.append('Goal and Increment must be numeric')
        
        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO habits (Name, Goal, Increment, Unit) VALUES (?, ?, ?, ?)", (name, goal, increment, unit))
            conn.commit()
            conn.close()

            return redirect(url_for('home'))

    return render_template('AddHabit.html')

@app.route('/ManageHabit.html', methods=['GET'])
@app.route('/ManageHabit/<int:year>/<int:month>', methods=['GET', 'POST'])
def manage_habit(year=None, month=None):
    habit_id = request.args.get('id', type=int)
    errors = []
    habit = None

    if habit_id:
        habit = get_habit_by_id(habit_id) 
        if not habit:
            errors.append('Habit not found')

    # Calendar setup
    current_date = datetime(year or datetime.today().year, month or datetime.today().month, 1)
    calendar_data = get_calendar_data(current_date)

    if request.method == 'POST':
        action = request.form.get('action', '')
        id = request.form.get('habit_id', type=int)

        if action == 'delete':
            if id:
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM habits WHERE id = ?", (id,))
                    conn.commit()
                    return redirect(url_for('home'))
                except Exception as e:
                    conn.rollback()
                    errors.append(f"Database error: {e}")
                finally:
                    conn.close()
            else:
                errors.append("Missing Habit ID to delete")
            return render_template('ManageHabit.html', calendar_data=calendar_data, current_date=current_date, habit=habit, errors=errors)
        
        name = request.form['name'].strip()
        goal = request.form['goal']
        increment = request.form['increment']
        unit = request.form['unit']

        if not name:
            errors.append('Name is required')

        try:
            goal = int(goal)
            increment = int(increment)
            if increment <= 0:
                errors.append('Increment must be greater than 0')
        except ValueError:
            errors.append('Goal and Increment must be numeric')

        if errors:
            return render_template('ManageHabit.html', calendar_data=calendar_data, current_date=current_date, habit=habit, errors=errors)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE habits SET Name = ?, Goal = ?, Increment = ?, Unit = ? WHERE id = ?",
                (name, goal, increment, unit, id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            errors.append(f"Database error: {e}")
        finally:
            conn.close()
                
        if errors:
            return render_template('ManageHabit.html', calendar_data=calendar_data, current_date=current_date, habit=habit, errors=errors)

        return redirect(url_for('home'))
    
    return render_template('ManageHabit.html', calendar_data=calendar_data, current_date=current_date, habit=habit)

@app.route('/increment/<int:habit_id>', methods=['POST'])
def increment_habit(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT progress, goal, increment FROM habits WHERE id = ?", (habit_id,))
    habit = cursor.fetchone()

    if habit and habit["progress"] < habit["goal"]:
        new_progress = habit["progress"] + habit["increment"]
        if new_progress > habit["goal"]:
            new_progress = habit["goal"]
            print(new_progress)
        cursor.execute(
            "UPDATE habits SET progress = ? WHERE id = ?",
            (new_progress, habit_id)
        )
        conn.commit()

        return jsonify({"success": True, "Progress": new_progress})

    return jsonify({"success": False, "message": "Cannot decrement progress."})

@app.route('/decrement/<int:habit_id>', methods=['POST'])
def decrement_habit(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT progress, increment FROM habits WHERE id = ?", (habit_id,))
    habit = cursor.fetchone()

    if habit and habit["progress"] > 0:
        new_progress = habit["progress"] - habit["increment"]
        if new_progress < 0:
            new_progress = 0
        cursor.execute(
            "UPDATE habits SET progress = ? WHERE id = ?",
            (new_progress, habit_id)
        )
        conn.commit()

        return jsonify({"success": True, "Progress": new_progress})

    return jsonify({"success": False, "message": "Cannot decrement progress."})

@app.route('/Goal.html')
def goal():
    return render_template('Goal.html')

@app.route('/Finance.html')
def finance():
    return render_template('Finance.html')

@app.route('/Fitness.html')
def fitness():
    return render_template('Fitness.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=55557, debug=True)
