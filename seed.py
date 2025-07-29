from app import app, db
from models import User, ParkingLot, ParkingSpot
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Check if user already exists
    if not User.query.filter_by(email='test@example.com').first():
        user = User(
            username='testuser',
            email='test@example.com',
            passkey=generate_password_hash('test123', method='pbkdf2:sha256'),
            full_name='Test User',
            phone_number='9999999999'
        )
        db.session.add(user)
        db.session.commit()

        lot = ParkingLot(
            prime_location_name='MG Road',
            address='MG Road, Bengaluru',
            pin_code='560001',
            price_per_hour=30.00,
            maximum_number_of_spots=5,
            current_available_spots=5,
            created_by=user.id
        )
        db.session.add(lot)
        db.session.commit()

        for i in range(1, 6):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f"MG-{i}",
                status='A',
                is_active=True
            )
            db.session.add(spot)

        db.session.commit()
        print("Test data inserted successfully.")
    else:
        print("Test user already exists. No data inserted.")
