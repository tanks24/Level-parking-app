# db.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)


db = SQLAlchemy(app)
