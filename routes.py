from flask import Blueprint, request, render_template, redirect, url_for, flash
from models import User, Admin
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

routes = Blueprint('routes', __name__)

@routes.route("/")
def home():
    return render_template("main.html")

@routes.route("/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("passkey")
        full_name = request.form.get("full_name")
        phone_number = request.form.get("phone_number")
        role = request.form.get("role", "USER").upper()

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
        ).first()
        if existing_user:
            flash("User already exists. Please login.", "warning")
            return redirect(url_for("routes.login"))

        new_user = User(
            username=username,
            email=email,
            passkey=hashed_password,
            full_name=full_name,
            phone_number=phone_number,
            rolle="USER",
            registration_date=datetime.utcnow()
        )
        db.session.add(new_user)

        db.session.commit()

        flash(f"{role.capitalize()} registration successful. Please login.", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html")


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("passkey")

        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.passkey, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("routes.user_dashboard"))

        
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("routes.admin_dashboard"))

        
        flash("Invalid email or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")



@routes.route("/user/dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html", username=current_user.username)


@routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if hasattr(current_user, 'role_type') and current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))
    return render_template("admin_dashboard.html", username=current_user.username)


@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.login"))


@routes.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.rolle
            } for u in users
        ]
    }
