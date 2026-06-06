from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "attendance123"

# ---------------- DATABASE ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = sqlite3.connect(os.path.join(BASE_DIR, "attendance.db"), check_same_thread=False)
cursor = db.cursor()

# ---------------- TABLES ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# default admin
cursor.execute("SELECT * FROM admin")
if not cursor.fetchone():
    cursor.execute("INSERT INTO admin(username, password) VALUES (?,?)",
                   ("admin", "admin123"))
    db.commit()

db.commit()

# ---------------- HOME ---------------- #

@app.route('/')
def home():
    return render_template("index.html")

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute("""
        INSERT INTO students(name, email, password)
        VALUES (?, ?, ?)
        """, (name, email, password))

        db.commit()
        return redirect('/login')

    return render_template("register.html")

# ---------------- STUDENT LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("""
        SELECT * FROM students
        WHERE email=? AND password=?
        """, (email, password))

        user = cursor.fetchone()

        if user:
            session['student_id'] = user[0]
            session['name'] = user[1]
            return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template("login.html")

# ---------------- ADMIN LOGIN ---------------- #

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("""
        SELECT * FROM admin
        WHERE username=? AND password=?
        """, (username, password))

        admin = cursor.fetchone()

        if admin:
            session['admin'] = True
            return redirect('/admin_dashboard')

        return "Invalid Admin Login"

    return render_template("admin.html")

# ---------------- STUDENT DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if 'student_id' not in session:
        return redirect('/login')

    cursor.execute("""
    SELECT attendance_date, status
    FROM attendance
    WHERE student_id=?
    ORDER BY attendance_date DESC
    """, (session['student_id'],))

    records = cursor.fetchall()

    return render_template("dashboard.html",
                           name=session['name'],
                           records=records)

# ---------------- MARK ATTENDANCE ---------------- #

@app.route('/mark')
def mark():

    if 'student_id' not in session:
        return redirect('/login')

    student_id = session['student_id']
    today = str(date.today())

    cursor.execute("""
    SELECT * FROM attendance
    WHERE student_id=? AND attendance_date=?
    """, (student_id, today))

    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO attendance(student_id, attendance_date, status)
        VALUES (?, ?, ?)
        """, (student_id, today, "Present"))
        db.commit()

    return redirect('/dashboard')

# ---------------- ADMIN DASHBOARD ---------------- #

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("SELECT id, name, email FROM students")
    students = cursor.fetchall()

    return render_template("admin_dashboard.html", students=students)

# ---------------- FULL ATTENDANCE VIEW (IMPORTANT) ---------------- #

@app.route('/admin_attendance')
def admin_attendance():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("""
    SELECT students.name,
           students.email,
           attendance.attendance_date,
           attendance.status
    FROM attendance
    JOIN students ON attendance.student_id = students.id
    ORDER BY attendance.attendance_date DESC
    """)

    records = cursor.fetchall()

    return render_template("admin_attendance.html", records=records)

# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
