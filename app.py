from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "attendance123"

# SQLite Database Connection
db = sqlite3.connect("attendance.db", check_same_thread=False)
cursor = db.cursor()

# Create Students Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

# Create Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT
)
""")

db.commit()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        sql = """
        INSERT INTO students(name,email,password)
        VALUES(?,?,?)
        """

        cursor.execute(sql, (name, email, password))
        db.commit()

        return redirect('/login')

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM students
        WHERE email=? AND password=?
        """

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:
            session['student_id'] = user[0]
            session['name'] = user[1]

            return redirect('/dashboard')

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():

    if 'student_id' not in session:
        return redirect('/login')

    student_id = session['student_id']

    sql = """
    SELECT attendance_date,status
    FROM attendance
    WHERE student_id=?
    """

    cursor.execute(sql, (student_id,))
    records = cursor.fetchall()

    return render_template(
        "dashboard.html",
        name=session['name'],
        records=records
    )


@app.route('/mark')
def mark():

    if 'student_id' not in session:
        return redirect('/login')

    student_id = session['student_id']

    sql = """
    INSERT INTO attendance(
    student_id,
    attendance_date,
    status)
    VALUES(?,?,?)
    """

    cursor.execute(
        sql,
        (student_id, str(date.today()), "Present")
    )

    db.commit()

    return redirect('/dashboard')


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)