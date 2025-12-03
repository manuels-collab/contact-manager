from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, String, Integer, Float, LargeBinary, insert, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates, Session, sessionmaker
import os
load_dotenv()
#Using SQLACLHEMY ORM STYLE
connection_string = URL.create(
"mysql+mysqldb",
    port = os.getenv("DB_PORT"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
    username = os.getenv("DB_USERNAME"),
    database = os.getenv("DB_NAME")
)

class MyBase(DeclarativeBase):
    pass

engine = create_engine(connection_string, echo=True)

PROFILE_IMAGE_SIZE = 1 * (1024 * 1024)


class ContactManager(MyBase):
    __tablename__ = "contact_manager"

    name: Mapped[str] = mapped_column(String(45), nullable=False)
    phone: Mapped[int] = mapped_column(Integer, primary_key=True)
    address = mapped_column(String(45), nullable=False)
    email: Mapped[str] = mapped_column(String(30), primary_key=True)
    profile_picture = mapped_column(LargeBinary(length=PROFILE_IMAGE_SIZE), nullable=False)

    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address:
            raise ValueError("Not a valid email address")
        return address

def load_image(path: str) -> bytes:
    with open(path, "rb") as img:
        return img.read()

