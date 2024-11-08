from .models import Vehicles, Services
from .extensions import db
import bleach


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


def validate_delete(user_id, delete_id, type):
    """Verifies delete comes from user who owns | Returns False for non user delete attempt & Returns db col to delete
    for validated user | args: user_id -> current user id & delete_id -> database col id to delete & type -> which table
    | if type is vehicle wipes services from database"""
    if type == 'vehicle':
        to_delete = db.session.execute(db.Select(Vehicles).where(Vehicles.id == delete_id)).scalar()
        if to_delete.owner_id == user_id:
            wipe_services(to_delete.services)
            return to_delete
        else:
            return False
    elif type == 'service':
        to_delete = db.session.execute(db.Select(Services).where(Services.id == delete_id)).scalar()
        if to_delete.owner_id == user_id:
            return to_delete
        else:
            return False


def validate_data_request(user_id, data_id, type):
    """Verifies data request comes from user who owns | Returns False for non user data request & database column
    for validated user | args: user_id -> current user id & data_id -> database col id to grab data & type -> which table"""
    if type == 'vehicle':
        data_grab = db.session.execute(db.Select(Vehicles).where(Vehicles.id == data_id)).scalar()
        if data_grab.owner_id == user_id:
            return data_grab
        else:
            return False
    elif type == 'service':
        data_grab = db.session.execute(db.Select(Services).where(Services.id == data_id)).scalar()
        if data_grab.owner_id == user_id:
            return data_grab
        else:
            return False
