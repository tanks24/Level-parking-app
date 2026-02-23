from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from models import User, Admin , ParkingLot , ParkingSpot, Reservation
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

@routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if hasattr(current_user, 'role_type') and current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    lots = ParkingLot.query.all()

    total_spots = db.session.query(ParkingSpot).count()
    occupied_spots = db.session.query(ParkingSpot).filter_by(is_occupied=True).count()
    available_spots = total_spots - occupied_spots
    return render_template(
        "admin_dashboard.html",
        username=current_user.username,
        lots=lots,
        total_spots=total_spots,
        occupied_spots=occupied_spots,
        available_spots=available_spots
    )

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
@routes.route("/admin/users")
@login_required
def view_users():
    if current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    users = User.query.all()

    user_data = []
    for user in users:
        data = {
            "username": user.username,
            "reservations": user.reservations 
        }
        user_data.append(data)

    return render_template("view_users.html", users=user_data)

@routes.route("/admin/create_lot", methods=["GET", "POST"])
@login_required
def create_lot():
    if current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = request.form['price']

        try:
            capacity = int(request.form['capacity'])
        except ValueError:
            flash("Capacity must be a valid number.")
            return redirect(url_for("routes.create_lot"))

        lot = ParkingLot(
            prime_location_name=name,
            address=address,
            pin_code=pin_code,
            price_per_hour=price,
            maximum_number_of_spots=capacity,
            current_available_spots=capacity,
            is_active=True,
            created_date=datetime.utcnow(),
            last_modified=datetime.utcnow()
        )
        db.session.add(lot)
        db.session.commit()

        for i in range(1, capacity + 1):
            spot = ParkingSpot(lot_id=lot.id, spot_number=f"S{i}", is_occupied=False)
            db.session.add(spot)

        db.session.commit()
        flash("Lot created with spots.")
        return redirect(url_for('routes.admin_dashboard'))

    return render_template("create_lot.html")

@routes.route("/admin/lot/<int:lot_id>")
@login_required
def view_lot(lot_id):
    if current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template("view_lot.html", lot=lot, spots=spots)

@routes.route("/admin/edit_lot/<int:lot_id>", methods=["GET", "POST"])
@login_required
def edit_lot(lot_id):
    if current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == "POST":
        lot.prime_location_name = request.form["name"]
        lot.address = request.form["address"]
        lot.pin_code = request.form["pin_code"]
        lot.price_per_hour = request.form["price"]
        db.session.commit()
        flash("Parking lot updated successfully!")
        return redirect(url_for('routes.admin_dashboard'))

    return render_template("edit_lot.html", lot=lot)

@routes.route("/admin/delete_lot/<int:lot_id>")
@login_required
def delete_lot(lot_id):
    if current_user.role_type != 'admin':
        return redirect(url_for('routes.user_dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)
    ParkingSpot.query.filter_by(lot_id=lot.id).delete() 
    db.session.delete(lot)
    db.session.commit()
    flash("Lot and its spots deleted.")
    return redirect(url_for('routes.admin_dashboard'))

@routes.route("/user/dashboard")
@login_required
def user_dashboard():
    lots = ParkingLot.query.all()
    active_reservation = Reservation.query.filter_by(user_id=current_user.id, status="active").first()

    reserved_spot = None
    if active_reservation:
        reserved_spot = ParkingSpot.query.get(active_reservation.spot_id)

    return render_template(
        "user_dashboard.html", 
        lots=lots, 
        active_reservation=active_reservation,
        reserved_spot=reserved_spot,
        username=current_user.username 
    )

@routes.route("/reserve/<int:lot_id>", methods=["POST"])
@login_required
def reserve_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if lot.current_available_spots < 1:
        flash("No available spots in this lot.", "error")
        return redirect(url_for("routes.user_dashboard"))
    existing = Reservation.query.filter_by(user_id=current_user.id, status="active").first()
    if existing:
        flash("You already have an active reservation.", "error")
        return redirect(url_for("routes.user_dashboard"))
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").first()
    if not spot:
        flash("No available spot found.", "error")
        return redirect(url_for("routes.user_dashboard"))
    spot.status = "active"
    lot.current_available_spots -= 1

    reservation = Reservation(
        user_id=current_user.id,
        spot_id=spot.id,
        lot_id=lot.id,
        parking_timestamp=datetime.utcnow(),  # Directly set parking time
        status="active",
        hourly_rate=lot.price_per_hour
    )
    db.session.add(reservation)
    db.session.commit()
    flash(f"Spot {spot.spot_number} reserved and occupied successfully!", "success")
    return redirect(url_for("routes.user_dashboard"))


@routes.route("/release/<int:reservation_id>", methods=["POST"])
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.id:
        abort(403)

    if reservation.status != "active":
        flash("You can only release an active reservation.", "warning")
        return redirect(url_for('routes.user_dashboard'))
    if not reservation.parking_timestamp:
        flash("You haven't occupied this spot yet.", "warning")
        return redirect(url_for('routes.user_dashboard'))
    if reservation.leaving_timestamp:
        flash("This spot has already been released.", "info")
        return redirect(url_for('routes.user_dashboard'))
    reservation.leaving_timestamp = datetime.utcnow()
    reservation.status = "completed"
    reservation.spot.status = "A"
    if reservation.lot.current_available_spots is not None:
        reservation.lot.current_available_spots += 1
    time_diff_hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    reservation.total_cost = round(time_diff_hours-1 * float(reservation.hourly_rate), 2)
    base = 1.5* float(reservation.hourly_rate)
    reservation.total_cost = base + reservation.total_cost

    db.session.commit()

    flash(f"Spot released. Total cost: ₹{reservation.total_cost}", "info")
    return redirect(url_for('routes.user_dashboard'))


@routes.route('/user/history')
@login_required
def view_parking_history():
    history = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template("parking_history.html", reservations=history)

def calculate_cost(reservation):
    if reservation.parking_timestamp and reservation.leaving_timestamp:
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        total_seconds = duration.total_seconds()
        hours = total_seconds / 3600
        base = 1.5* float(reservation.hourly_rate)
      
        cost = round(hours * float(reservation.hourly_rate-1), 2)
        cost = base + cost 
        return cost
    return 0.0