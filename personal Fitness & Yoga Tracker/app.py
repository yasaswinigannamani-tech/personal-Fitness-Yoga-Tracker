# app.py
"""Personal Fitness & Yoga Tracker - Main Application
Project 13 | Health & Wellness + Programming + Communicative English

Topics Integrated:
- Yoga practices (asana logging)
- Arrays (data structures for plans)
- Technical writing (documentation & reports)
- SQL Database (sqlite3)
- Simple menu system (web-based navigation)
"""

import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

from llm_engine import generate_weekly_plan, analyze_progress

app = Flask(__name__)
app.secret_key = "yoga_tracker_secret_key_2024"

# Database setup
DB_NAME = "yoga_tracker.db"

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            goal TEXT NOT NULL,
            time_per_day INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            asana TEXT NOT NULL,
            english_name TEXT,
            date TEXT NOT NULL,
            duration INTEGER NOT NULL,
            intensity INTEGER NOT NULL,
            notes TEXT,
            mood TEXT,
            logged_at TEXT NOT NULL,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_current_user():
    """Get current logged-in user data from SQL."""
    if "user_email" not in session:
        return None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (session["user_email"],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)  # Convert sqlite3.Row to dictionary
    return None

# ============ ROUTES (Menu System) ============

@app.route("/")
def index():
    """Home page - Dashboard."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    
    # Get user's logs using SQL
    cursor.execute('''
        SELECT * FROM logs 
        WHERE user_email = ? 
        ORDER BY date DESC, logged_at DESC 
        LIMIT 5
    ''', (session["user_email"],))
    recent_logs = [dict(row) for row in cursor.fetchall()]
    
    # Get all logs for stats
    cursor.execute("SELECT * FROM logs WHERE user_email = ?", (session["user_email"],))
    all_logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    stats = analyze_progress(all_logs)

    return render_template("index.html", user=user, stats=stats, recent_logs=recent_logs)


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login / registration."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip()
        level = request.form.get("level", "beginner")
        goal = request.form.get("goal", "general")
        time_per_day = int(request.form.get("time_per_day", 30))

        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user exists (SQL SELECT)
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Insert new user (SQL INSERT)
            cursor.execute('''
                INSERT INTO users (email, name, level, goal, time_per_day, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, name if name else "Yogi", level, goal, time_per_day, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            flash("Account created! Welcome to your yoga journey. 🧘", "success")
        else:
            flash(f"Welcome back, {existing_user['name']}! 🙏", "info")

        session["user_email"] = email
        conn.close()
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout user."""
    session.pop("user_email", None)
    flash("Logged out successfully. Namaste! 🙏", "info")
    return redirect(url_for("login"))


@app.route("/log_practice", methods=["GET", "POST"])
def log_practice():
    """Log a yoga practice session."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        asana = request.form.get("asana", "").strip()
        english_name = request.form.get("english_name", "").strip()
        date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
        duration = int(request.form.get("duration", 15))
        intensity = int(request.form.get("intensity", 3))
        notes = request.form.get("notes", "").strip()
        mood = request.form.get("mood", "neutral")

        conn = get_db()
        cursor = conn.cursor()
        
        # Insert log into SQL database
        cursor.execute('''
            INSERT INTO logs (user_email, asana, english_name, date, duration, intensity, notes, mood, logged_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session["user_email"], asana, english_name, date, duration, intensity, notes, mood,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        flash(f"Practice logged: {asana} for {duration} minutes! 🌟", "success")
        return redirect(url_for("progress"))

    common_asanas = [
        ("Tadasana", "Mountain Pose"), ("Vrikshasana", "Tree Pose"),
        ("Bhujangasana", "Cobra Pose"), ("Adho Mukha Svanasana", "Downward Dog"),
        ("Trikonasana", "Triangle Pose"), ("Virabhadrasana", "Warrior Pose"),
        ("Balasana", "Child's Pose"), ("Setu Bandhasana", "Bridge Pose"),
        ("Savasana", "Corpse Pose"), ("Surya Namaskar", "Sun Salutation"),
        ("Dhanurasana", "Bow Pose"), ("Padmasana", "Lotus Pose"),
    ]

    return render_template("log_practice.html", asanas=common_asanas,
                           today=datetime.now().strftime("%Y-%m-%d"))


@app.route("/weekly_plan")
def weekly_plan():
    """Generate weekly plan using LLM engine."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs WHERE user_email = ?", (session["user_email"],))
    my_logs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    plan_data = generate_weekly_plan(user, my_logs)

    return render_template("weekly_plan.html", user=user, plan_data=plan_data)


@app.route("/progress")
def progress():
    """View progress and statistics."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    
    # Get all logs ordered by date descending
    cursor.execute('''
        SELECT * FROM logs 
        WHERE user_email = ? 
        ORDER BY date DESC, logged_at DESC
    ''', (session["user_email"],))
    my_logs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    stats = analyze_progress(my_logs)

    return render_template("progress.html", user=user, stats=stats, logs=my_logs)


@app.route("/delete_log/<int:log_id>")
def delete_log(log_id):
    """Delete a practice log entry using SQL DELETE."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    
    # Delete specifically by ID AND user_email for security
    cursor.execute("DELETE FROM logs WHERE id = ? AND user_email = ?", 
                   (log_id, session["user_email"]))
    conn.commit()
    conn.close()
    
    flash("Practice log deleted.", "info")
    return redirect(url_for("progress"))


@app.route("/about")
def about():
    """About page - Technical writing documentation."""
    return render_template("about.html")


@app.route("/update_profile", methods=["POST"])
def update_profile():
    """Update user profile settings using SQL UPDATE."""
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    level = request.form.get("level", user["level"])
    goal = request.form.get("goal", user["goal"])
    time_per_day = int(request.form.get("time_per_day", 30))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET level = ?, goal = ?, time_per_day = ? 
        WHERE email = ?
    ''', (level, goal, time_per_day, session["user_email"]))
    conn.commit()
    conn.close()

    flash("Profile updated! 🎯", "success")
    return redirect(url_for("index"))


# ============ MAIN ENTRY POINT ============

if __name__ == "__main__":
    init_db()  # Initialize database before starting server
    print("=" * 60)
    print("  Personal Fitness & Yoga Tracker - Project 13")
    print("=" * 60)
    print("  Server starting at: http://127.0.0.1:5000")
    print("  Database: SQLite (yoga_tracker.db)")
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)