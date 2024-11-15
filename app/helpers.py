from wtforms import FileField
import bleach
from io import BytesIO
from PIL import Image
from .models import Vehicles, Services
from .extensions import db


def sanitize_html(html):
    """Sanitizes html from CKEDITOR field to protect from script injection"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'h1', 'h2', 'h3']
    allowed_attrs = {'a': ['href', 'title']}
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return clean_html


def wipe_services(services):
    """delete all service for a vehicle NO VALIDATION ON USER"""
    for service in services:
        db.session.delete(service)
    db.session.commit()


def validate_delete_request(user_id, delete_id, table):
    """Verifies delete comes from user who owns | Returns False for non user delete attempt & Returns db col to delete
    for validated user | args: user_id -> current user id & delete_id -> database col id to delete & type -> which table
    | if type is vehicle wipes services from database"""
    if table == 'vehicle':
        to_delete = db.session.execute(db.Select(Vehicles).where(Vehicles.id == delete_id)).scalar()
        if to_delete.owner_id == user_id:
            wipe_services(to_delete.services)
            return to_delete
        else:
            return False
    elif table == 'service':
        to_delete = db.session.execute(db.Select(Services).where(Services.id == delete_id)).scalar()
        if to_delete.owner_id == user_id:
            return to_delete
        else:
            return False


def validate_data_request(user_id, db_id, table):
    """Verifies data request comes from user who owns | Returns False for non user data request & database column
    for validated user | args: user_id -> current user id & data_id -> database col id to grab data & type -> which table"""
    if table == 'vehicle':
        data_grab = db.session.execute(db.Select(Vehicles).where(Vehicles.id == db_id)).scalar()
        if data_grab.owner_id == user_id:
            return data_grab
        else:
            return False
    elif table == 'service':
        data_grab = db.session.execute(db.Select(Services).where(Services.id == db_id)).scalar()
        if data_grab.owner_id == user_id:
            return data_grab
        else:
            return False


def save_to_db(model: db.Model, data):
    try:
        required_columns = model.__table__.columns.keys()[1:]
        print(required_columns)
        packaged_data = {col_name: data[col_name] for col_name in required_columns}
        new_row = model(**packaged_data)
        db.session.add(new_row)
    except Exception as e:
        print(e)
        return False
    else:
        print("Y")
        db.session.commit()
        return new_row


def retrieve_from_db(model: db.Model, id):
    row = db.session.execute(db.Select(model).where(model.id == id)).scalar()
    if row:
        return row
    return False


def update_record(model: db.Model, row, data):
    try:
        for col, value in data.items():
            if col in model.__table__.columns.keys():
                setattr(row, col, value)
    except Exception as e:
        print(f"FAILURE TO UPDATE RECORD {row} ERROR: {e}")
        db.session.rollback()
        return False
    else:
        db.session.commit()
        return True


def is_empty_field(field):
    if isinstance(field, FileField):
        print("Y")
        if field.data.filename == "":
            return True
    if field.data == "":
        return True
    return False


def blob_to_file(blob):
    bytes_io = BytesIO(blob)
    bytes_io.seek(0)
    return bytes_io


def file_to_blob(file):
    binary_data = file.read()
    img = Image.open(BytesIO(binary_data))
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, 'white')
        # Handle transparency by placing on white background
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != 'RGB':
        # Convert any other modes to RGB
        img = img.convert('RGB')
    img.thumbnail(size=(200, 200))
    thumb_io = BytesIO()
    img.save(thumb_io, 'JPEG', quality=85)
    return thumb_io.getvalue()
