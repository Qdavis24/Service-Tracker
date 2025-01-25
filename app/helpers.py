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


def validate_delete_request(user_id: int, delete_id: int, table: str):
    """retrieves row from database to delete, verifies row belongs to request source, deletes all children connected to
     'to delete', returns to delete row |
    ARGS: user_id -> current user id & delete_id -> database col id to delete & table -> which table
    RETURNS: requested deletion row for success & False for failure"""

    if table == 'vehicle':
        to_delete_vehicle = db.session.execute(db.Select(Vehicles).where(Vehicles.id == delete_id)).scalar()
        if not to_delete_vehicle.owner_id == user_id:
            return False
        return to_delete_vehicle

    elif table == 'service':
        to_delete_service = db.session.execute(db.Select(Services).where(Services.id == delete_id)).scalar()
        if not to_delete_service.owner_id == user_id:
            return False
        return to_delete_service


def validate_data_request(user_id: int, db_id: int, table: db.Model):
    """
    ARGS: user_id -> current user id & data_id -> target database col id & table -> which table
    RETURNS: requested data for success & False for failure"""
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


def save_to_db(table: db.Model, data: dict):
    try:
        required_columns = table.__table__.columns.keys()[1:]
        packaged_data = {col_name: data[col_name] for col_name in required_columns}
        new_row = table(**packaged_data)
        db.session.add(new_row)
    except Exception as e:
        print(e)
        return False
    else:
        db.session.commit()
        return new_row


def retrieve_from_db(table: db.Model, id: int):
    row = db.session.execute(db.Select(table).where(table.id == id)).scalar()
    if row:
        return row
    return False


def update_record(table: db.Model, row, data):
    try:
        for col, value in data.items():
            if col in table.__table__.columns.keys():
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
    if not file:
        print("early exit file to blob")
        return file
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
