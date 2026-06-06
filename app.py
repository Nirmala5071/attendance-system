from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "attendance123"

# Database Connection
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

conn.execute('''
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

conn.execute("""
INSERT OR IGNORE INTO admin
(id,username,password)
VALUES(1,'admin','admin123')
""")

conn.commit()

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Register Student
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

    return render_template('register.html')

# Students List
@app.route('/students')
def students():

    conn = get_db()

    data = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    return render_template(
        'students.html',
        students=data
    )

# Attendance Page
@app.route('/attendance')
def attendance():

    conn = get_db()

    data = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    return render_template(
        'attendance.html',
        students=data
    )

# Mark Attendance
@app.route('/mark/<int:id>')
def mark(id):

    conn = get_db()

    conn.execute(
        '''
        INSERT INTO attendance
        (student_id,att_date,status)
        VALUES(?,?,?)
        ''',
        (id,str(date.today()),"Present")
    )

    conn.commit()

    return redirect('/attendance')

# Reports
@app.route('/reports')
def reports():

    conn = get_db()

    report = conn.execute('''
    SELECT students.name,
           COUNT(attendance.id) as total
    FROM students
    LEFT JOIN attendance
    ON students.id=attendance.student_id
    GROUP BY students.id
    ''').fetchall()

    return render_template(
        'reports.html',
        reports=report
    )

# Admin Login
@app.route('/admin', methods=['GET','POST'])
def admin():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()

        admin = conn.execute(
        '''
        SELECT * FROM admin
        WHERE username=? AND password=?
        ''',
        (username,password)
        ).fetchone()

        if admin:

            session['admin'] = username

            return redirect('/admin_dashboard')

    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_attendance = conn.execute(
        "SELECT COUNT(*) FROM attendance"
    ).fetchone()[0]

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    attendance = conn.execute('''
    SELECT students.name,
           attendance.att_date,
           attendance.status
    FROM attendance
    JOIN students
    ON students.id = attendance.student_id
    ORDER BY attendance.att_date DESC
    ''').fetchall()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_attendance=total_attendance,
        students=students,
        attendance=attendance
    )

# Logout
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
