from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///attendance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20), default="student")  # admin/student


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(50))


# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            username=request.form["username"],
            password=request.form["password"],
            role="student"
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template_string("""
        <h2>Register</h2>
        <form method="post">
            Name: <input name="name"><br>
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <button type="submit">Register</button>
        </form>
        <a href="/login">Login</a>
    """)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect("/dashboard")

    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <button type="submit">Login</button>
        </form>
        <a href="/register">Register</a>
    """)


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    return render_template_string("""
        <h2>Welcome {{user.name}}</h2>

        <a href="/mark">Mark Attendance</a><br>

        {% if session['role'] == 'admin' %}
            <a href="/admin">Admin Dashboard</a><br>
        {% endif %}

        <a href="/logout">Logout</a>
    """, user=user)


# ---------------- MARK ATTENDANCE ----------------
@app.route("/mark")
def mark():
    if "user_id" not in session:
        return redirect("/login")

    today = datetime.now().strftime("%Y-%m-%d")

    existing = Attendance.query.filter_by(
        user_id=session["user_id"],
        date=today
    ).first()

    if not existing:
        att = Attendance(user_id=session["user_id"], date=today)
        db.session.add(att)
        db.session.commit()

    return "Attendance Marked for Today ✔ <br><a href='/dashboard'>Back</a>"


# ---------------- ADMIN DASHBOARD (NEW) ----------------
@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return "Access Denied"

    users = User.query.all()
    attendance = Attendance.query.all()

    return render_template_string("""
        <h2>Admin Dashboard</h2>

        <h3>Registered Users</h3>
        <ul>
        {% for u in users %}
            <li>{{u.id}} - {{u.name}} ({{u.username}}) - {{u.role}}</li>
        {% endfor %}
        </ul>

        <h3>Attendance Records</h3>
        <ul>
        {% for a in attendance %}
            <li>User ID: {{a.user_id}} | Date: {{a.date}}</li>
        {% endfor %}
        </ul>

        <a href="/dashboard">Back</a>
    """, users=users, attendance=attendance)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- CREATE DB ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # create default admin (only once)
        if not User.query.filter_by(username="admin").first():
            admin = User(name="Admin", username="admin", password="admin", role="admin")
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
