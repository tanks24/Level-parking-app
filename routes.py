from flask import Blueprint, jsonify
from models import User

routes = Blueprint('routes', __name__)

@routes.route("/users")
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username} for u in users])