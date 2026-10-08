from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for login session
app.secret_key = "essential-public-services-secret-key"

# Database path
DATABASE = "database.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_db():
    conn = get_db_connection()

    # Facilities table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            opening_hours TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Admin table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create default admin if no admin exists
    admin = conn.execute(
        "SELECT * FROM admins WHERE username = ?",
        ("admin",)
    ).fetchone()

    if admin is None:
        password = generate_password_hash("admin123")

        conn.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            ("admin", password)
        )

    conn.commit()
    conn.close()


# --------------------------------------------------
# LOGIN REQUIRED DECORATOR
# --------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "admin_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():

    conn = get_db_connection()

    facilities = conn.execute("""
        SELECT * FROM facilities
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        facilities=facilities
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()

        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if admin and check_password_hash(admin["password"], password):

            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]

            flash("Login successful.", "success")

            return redirect(url_for("admin"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("index"))


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
@login_required
def admin():

    conn = get_db_connection()

    facilities = conn.execute("""
        SELECT * FROM facilities
        ORDER BY id DESC
    """).fetchall()

    total_facilities = conn.execute(
        "SELECT COUNT(*) FROM facilities"
    ).fetchone()[0]

    total_hospitals = conn.execute(
        "SELECT COUNT(*) FROM facilities WHERE category = ?",
        ("Hospital",)
    ).fetchone()[0]

    total_schools = conn.execute(
        "SELECT COUNT(*) FROM facilities WHERE category = ?",
        ("School",)
    ).fetchone()[0]

    total_police = conn.execute(
        "SELECT COUNT(*) FROM facilities WHERE category = ?",
        ("Police Station",)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        facilities=facilities,
        total_facilities=total_facilities,
        total_hospitals=total_hospitals,
        total_schools=total_schools,
        total_police=total_police
    )


# --------------------------------------------------
# ADD FACILITY
# --------------------------------------------------

@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def add_facility():

    if request.method == "POST":

        name = request.form.get("name")
        category = request.form.get("category")
        address = request.form.get("address")
        phone = request.form.get("phone")
        description = request.form.get("description")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        opening_hours = request.form.get("opening_hours")

        # Convert empty coordinates to None
        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO facilities
            (
                name,
                category,
                address,
                phone,
                description,
                latitude,
                longitude,
                opening_hours
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            address,
            phone,
            description,
            latitude,
            longitude,
            opening_hours
        ))

        conn.commit()
        conn.close()

        flash("Facility added successfully.", "success")

        return redirect(url_for("admin"))

    return render_template("add_facility.html")


# --------------------------------------------------
# EDIT FACILITY
# --------------------------------------------------

@app.route("/admin/edit/<int:facility_id>", methods=["GET", "POST"])
@login_required
def edit_facility(facility_id):

    conn = get_db_connection()

    facility = conn.execute(
        "SELECT * FROM facilities WHERE id = ?",
        (facility_id,)
    ).fetchone()

    if facility is None:

        conn.close()

        flash("Facility not found.", "danger")

        return redirect(url_for("admin"))

    if request.method == "POST":

        name = request.form.get("name")
        category = request.form.get("category")
        address = request.form.get("address")
        phone = request.form.get("phone")
        description = request.form.get("description")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        opening_hours = request.form.get("opening_hours")

        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None

        conn.execute("""
            UPDATE facilities
            SET
                name = ?,
                category = ?,
                address = ?,
                phone = ?,
                description = ?,
                latitude = ?,
                longitude = ?,
                opening_hours = ?
            WHERE id = ?
        """, (
            name,
            category,
            address,
            phone,
            description,
            latitude,
            longitude,
            opening_hours,
            facility_id
        ))

        conn.commit()
        conn.close()

        flash("Facility updated successfully.", "success")

        return redirect(url_for("admin"))

    conn.close()

    return render_template(
        "edit_facility.html",
        facility=facility
    )


# --------------------------------------------------
# DELETE FACILITY
# --------------------------------------------------

@app.route("/admin/delete/<int:facility_id>", methods=["POST"])
@login_required
def delete_facility(facility_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM facilities WHERE id = ?",
        (facility_id,)
    )

    conn.commit()
    conn.close()

    flash("Facility deleted successfully.", "success")

    return redirect(url_for("admin"))


# --------------------------------------------------
# API FOR MAP / JAVASCRIPT
# --------------------------------------------------

@app.route("/api/facilities")
def api_facilities():

    conn = get_db_connection()

    facilities = conn.execute("""
        SELECT
            id,
            name,
            category,
            address,
            phone,
            description,
            latitude,
            longitude,
            opening_hours
        FROM facilities
        WHERE latitude IS NOT NULL
        AND longitude IS NOT NULL
    """).fetchall()

    conn.close()

    data = []

    for facility in facilities:

        data.append({
            "id": facility["id"],
            "name": facility["name"],
            "category": facility["category"],
            "address": facility["address"],
            "phone": facility["phone"],
            "description": facility["description"],
            "latitude": facility["latitude"],
            "longitude": facility["longitude"],
            "opening_hours": facility["opening_hours"]
        })

    return jsonify(data)


# --------------------------------------------------
# APPLICATION START
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )