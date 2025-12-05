from flask import current_app, Blueprint, request, jsonify
from sqlalchemy import select, update, delete
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

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    quality = 85
    max_width = 1200

    while True:
        width_ratio = max_width / float(img.size[0])
        resized_img = img.resize(
            (max_width, int(img.size[1] * width_ratio))
        )

        buffer = BytesIO()
        resized_img.save(
            buffer,
            format="PNG",
            optimize=True,
            quality=quality
        )
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
    username = StringField(
        "Username",
        [
            validators.Length(min=3, max=50, message="Username must be 3–50 chars"),
            validators.data_required(message="Username required"),
        ],
    )

    email = StringField(
        "Email",
        [
            validators.Email(message="Valid email required")
        ],
    )

    address = StringField(
        "Address",
        [
            validators.Length(min=4, message="Address required")
        ],
    )

    phone = StringField(
        "Phone",
        [
            validators.Length(min=10, max=15, message="Phone must be 10–15 digits")
        ],
    )


# ---------------- ROUTE: ADD USER ----------------
@main.route("/add_user", methods=["POST"])
def add_user():
    form = ContactManagerForm(request.form)

    if not form.validate():
        return jsonify({"errors": form.errors}), 400

    if "file" not in request.files:
        return jsonify({"error": "Profile image required"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        Image.open(file)
    except Exception:
        return jsonify({"error": "Uploaded file must be a valid image"}), 400

    file.seek(0)
    compressed_bytes = compress_image(file)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    try:
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

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()


# ---------------- ROUTE: GET USERS ----------------
@main.route("/get_users", methods=["GET"])
def get_users():
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    try:
        rows = session.scalars(select(ContactManager)).all()
        users = [r.to_dict() for r in rows]
        return jsonify({"users": users}), 200

    finally:
        session.close()


# ---------------- ROUTE: UPDATE USER ----------------
@main.route("/update_user/<user_id>", methods=["PUT"])
def update_user_item(user_id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    try:
        # Accept both JSON and form-data
        data = request.get_json() if request.is_json else request.form

        name = data.get("username")
        address = data.get("address")

        if not name and not address:
            return jsonify({"error": "No data provided"}), 400

        stmt = (
            update(ContactManager)
            .where(ContactManager.phone == user_id)
            .values(
                **{k: v for k, v in {"name": name, "address": address}.items() if v}
            )
        )

        session.execute(stmt)
        session.commit()

        return jsonify({"message": "Successfully updated"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()


@main.route('/delete_users', methods=["DELETE"])
def delete_all_users():

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    try:
        stmt = delete(ContactManager)

        session.execute(stmt)
        session.commit()

        return  jsonify({"message": 'All users dedleted succesfully'}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()
