from flask import current_app, session
from sqlalchemy import select


from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session

from .models import ContactManager
from PIL import Image
from io import BytesIO

main = Blueprint("main", __name__)

MAX_SIZE_MB = 2
MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

def compress_image(file):
    img = Image.open(file)

    if img.mode in ("JPG", "P"):
        img = img.convert("PNG")

    quality = 85
    max_width = 1200

    while True:
        # Resize
        width_percent = max_width / float(img.size[0])
        height = int(float(img.size[1]) * width_percent)
        resized_img = img.resize((max_width, height))

        # Save to buffer
        buffer = BytesIO()
        resized_img.save(buffer, format="PNG", optimize=True, quality=quality)
        size = buffer.tell()

        # If under 2MB, stop
        if size <= MAX_BYTES:
            buffer.seek(0)
            return buffer.read()

        # Otherwise compress more
        quality -= 10
        max_width -= 200

        # Safety stop
        if quality < 10 or max_width < 200:
            buffer.seek(0)
            return buffer.read()  # return best result even if still a bit > 2MB

@main.route("/add_user", methods=["POST"])
def add_user():
    from . import db

    session = current_app.session
    data = request.form
    file = request.files['file']


    compressed_bytes = compress_image(file)

    user = ContactManager(name=data["name"],phone=data['phone'], address=data['address'], profile_picture=compressed_bytes, email=data["email"])

    session.add(user)
    session.commit()

    return {"message": "user created"}


@main.route("/get_users", methods=['GET'])
def get_users():
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    stmt = select(ContactManager)
    rows = session.scalars(stmt).all()

    users = [r.to_dict() for r in rows]

    return {"users": users}

