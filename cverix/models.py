from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, String, Integer, Float, LargeBinary, insert, select
from sqlalchemy.orm import scoped_session, Mapped, mapped_column, validates, Session, sessionmaker, DeclarativeBase
import os
from flask import current_app, g
from PIL import Image
load_dotenv()
#Using SQLACLHEMY ORM STYLE


class MyBase(DeclarativeBase):
    pass


PROFILE_IMAGE_SIZE = 1 * (1024 * 1024)


class ContactManager(MyBase):
    __tablename__ = "contact_manager"

    name: Mapped[str] = mapped_column(String(45), nullable=False)
    phone: Mapped[int] = mapped_column(Integer, primary_key=True)
    address = mapped_column(String(45), nullable=False)
    email: Mapped[str] = mapped_column(String(30), primary_key=True)
    profile_picture: Mapped[bytes] = mapped_column(LargeBinary(length=PROFILE_IMAGE_SIZE), nullable=False)

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email
        }

    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address:
            raise ValueError("Not a valid email address")
        return address
def load_image(path: str) -> bytes:
    with open(path, "rb") as img:
        return img.read()


