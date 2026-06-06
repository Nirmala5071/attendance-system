from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create Tables
conn = get_db()

conn.execute('''
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
att_date TEXT,
status TEXT
)
''')

conn.commit()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        conn = get_db()

        conn.execute(
            "INSERT INTO students(name,email) VALUES (?,?)",
            (name,email)
        )

        conn.commit()

        return redirect('/students')

    return render_template("register.html")

@app.route('/students')
def students():

    conn = get_db()

    data = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    return render_template(
        "students.html",
        students=data
    )

@app.route('/attendance')
def attendance():

    conn = get_db()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    return render_template(
        "attendance.html",
        students=students
    )

@app.route('/mark/<int:id>')
def mark(id):

    conn = get_db()

    conn.execute(
        '''
        INSERT INTO attendance
        (student_id,att_date,status)
        VALUES (?,?,?)
        ''',
        (id,str(date.today()),"Present")
    )

    conn.commit()

    return redirect('/attendance')

@app.route('/reports')
def reports():

    conn = get_db()

    data = conn.execute('''
    SELECT students.name,
    COUNT(attendance.id) as total
    FROM students
    LEFT JOIN attendance
    ON students.id = attendance.student_id
    GROUP BY students.id
    ''').fetchall()

    return render_template(
        "reports.html",
        reports=data
    )

if __name__ == "__main__":
    app.run(debug=True)
