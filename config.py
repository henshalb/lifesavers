import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", 'somesecretkey')
    SQLALCHEMY_DATABASE_URI = "sqlite:///lifesavers.sqlite"
    DEBUG = True