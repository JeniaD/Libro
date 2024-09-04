import os
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = "SECRET"
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
UPLOAD_FOLDER = "static/uploads"
