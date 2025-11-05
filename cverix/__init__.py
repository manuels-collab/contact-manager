from .models import MyBase
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, String, Integer, Float, LargeBinary, insert, select
from sqlalchemy.orm import scoped_session, Mapped, mapped_column, validates, Session, sessionmaker, DeclarativeBase
import os
from .routes import main
db = SQLAlchemy()

def create_app(test_config=None):
    connection_string = URL.create(
        "mysql+mysqldb",
        port=os.getenv("DB_PORT"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        username=os.getenv("DB_USERNAME"),
        database=os.getenv("DB_NAME")
    )
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)


    engine = create_engine(connection_string, echo=True)

    # Create session
    SessionLocal = scoped_session(sessionmaker(bind=engine))

    # Create tables
    MyBase.metadata.create_all(engine)

    # Attach session to app (important)
    app.SessionLocal = SessionLocal

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

        # REGISTER BLUEPRINT HERE

    app.register_blueprint(main, url_prefix="/main")

    return app