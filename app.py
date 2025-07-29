from flask import Flask
from flask_login import LoginManager
from db import db
from models import User, Admin
from routes import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YourNewPassword@localhost/Vehicle_Tracking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(routes)

login_manager = LoginManager()
login_manager.login_view = "routes.login"
login_manager.login_message_category = "info"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith("user_"):
        actual_id = int(user_id.replace("user_", ""))
        user = User.query.get(actual_id)
        if user:
            user.role_type = 'user'
            return user

    elif user_id.startswith("admin_"):
        actual_id = int(user_id.replace("admin_", ""))
        admin = Admin.query.get(actual_id)
        if admin:
            admin.role_type = 'admin'
            return admin

    return None

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)