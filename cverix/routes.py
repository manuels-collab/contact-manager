from flask import current_app, Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session
from wtforms import Form, StringField, validators
from PIL import Image
from io import BytesIO

from .models import ContactManager

main = Blueprint("main", __name__)

MAX_SIZE_MB = 2
MAX_BYTES = MAX_SIZE_MB * 1024 * 1024


# ---------------- IMAGE COMPRESSION ----------------
def compress_image(file):
    img = Image.open(file)

    # Convert unsupported modes
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    quality = 85
    max_width = 1200

    while True:
        width_percent = max_width / float(img.size[0])
        height = int(float(img.size[1]) * width_percent)
        resized_img = img.resize((max_width, height))

        buffer = BytesIO()
        resized_img.save(buffer, format="PNG", optimize=True, quality=quality)
        size = buffer.tell()

        if size <= MAX_BYTES:
            buffer.seek(0)
            return buffer.read()

        quality -= 10
        max_width -= 200

        if quality < 10 or max_width < 200:
            buffer.seek(0)
            return buffer.read()


# ---------------- WTForms VALIDATION ----------------
class ContactManagerForm(Form):
    username = StringField("Username",
                           [validators.Length(min=3, max=50, message="Username must be 3–50 chars")])

    email = StringField("Email",
                        [validators.Email(message="Valid email required")])

    address = StringField("Address",
                          [validators.Length(min=4, message="Address required")])

    phone = StringField("Phone",
                        [validators.Length(min=10, max=15, message="Phone must be 10–15 digits")])


# ---------------- ROUTE: ADD USER ----------------
@main.route("/add_user", methods=["POST"])
def add_user():

    form = ContactManagerForm(request.form)

    # Validate form
    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    # Validate file
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Basic image validation
    try:
        Image.open(file)
    except Exception:
        return jsonify({"error": "Uploaded file must be an image"}), 400

    # Compress
    file.seek(0)
    compressed_bytes = compress_image(file)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    # Create new user
    user = ContactManager(
        name=form.username.data,
        phone=form.phone.data,
        address=form.address.data,
        email=form.email.data,
        profile_picture=compressed_bytes,
    )

    session.add(user)
    session.commit()

    return jsonify({"message": "User created successfully"}), 201


# ---------------- ROUTE: GET USERS ----------------
@main.route("/get_users", methods=["GET"])
def get_users():
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    stmt = select(ContactManager)
    rows = session.scalars(stmt).all()

    users = [r.to_dict() for r in rows]

    return jsonify({"users": users})
