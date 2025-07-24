from db import app, db
from routes import routes


app.register_blueprint(routes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
