from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from db import db

class User(db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    Passkey = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    Rolle = Column(String(20), default='USER')
    is_active = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    created_parking_lots = relationship("ParkingLot", back_populates="creator")
    reservations = relationship("Reservation", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.Email}')>"


class ParkingLot(db.Model):
    __tablename__ = "ParkingLot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prime_location_name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    pin_code = Column(String(10), nullable=False)
    price_per_hour = Column(DECIMAL(10, 2), nullable=False)
    maximum_number_of_spots = Column(Integer, nullable=False)
    current_available_spots = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('user.id'))
    last_modified = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="created_parking_lots")
    spots = relationship("ParkingSpot", back_populates="lot")
    reservations = relationship("Reservation", back_populates="lot")

    def __repr__(self):
        return f"<ParkingLot(location='{self.prime_location_name}', price_per_hour={self.price_per_hour})>"


class ParkingSpot(db.Model):
    __tablename__ = "ParkingSpot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey('ParkingLot.id'), nullable=False)
    spot_number = Column(String(20), nullable=False)
    status = Column(CHAR(1), default='A')  # A = Available, B = Booked, etc.
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_occupied = Column(DateTime)

    lot = relationship("ParkingLot", back_populates="spots")
    reservations = relationship("Reservation", back_populates="spot")

    def __repr__(self):
        return f"<ParkingSpot(spot_number='{self.spot_number}', status='{self.status}')>"


class Reservation(db.Model):
    __tablename__ = "Reservation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    spot_id = Column(Integer, ForeignKey('ParkingSpot.id'), nullable=False)
    lot_id = Column(Integer, ForeignKey('ParkingLot.id'), nullable=False)

    parking_timestamp = Column(DateTime, nullable=False)
    leaving_timestamp = Column(DateTime)
    booking_timestamp = Column(DateTime, default=datetime.utcnow)

    hourly_rate = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2))
    status = Column(String(20), default='active')  # active, completed, cancelled
    vehicle_number = Column(String(20))

    user = relationship("User", back_populates="reservations")
    spot = relationship("ParkingSpot", back_populates="reservations")
    lot = relationship("ParkingLot", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(user_id={self.user_id}, spot_id={self.spot_id}, vehicle_number='{self.vehicle_number}')>"


class Admin(db.Model):
    __tablename__ = "Admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    is_super_admin = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Admin(username='{self.username}', email='{self.email}')>"
