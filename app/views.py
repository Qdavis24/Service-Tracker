from flask import Blueprint, render_template, redirect, request, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, and_, or_
from .helpers import validate_delete_request, validate_data_request, save_to_db, retrieve_from_db, update_record, \
    is_empty_field, blob_to_file, file_to_blob, sanitize_html
from .models import Vehicles, Users, Services, Pictures
from .forms import LoginForm, RegistrationForm, AddVehicleForm, EditVehicleForm, AddServiceForm

main_bp = Blueprint("main", __name__, template_folder="../templates")
api_bp = Blueprint("api", __name__, template_folder="../templates")


@main_bp.route("/", methods=["GET"])
def index(registration_form=None, login_form=None, modal_state=0):
    if current_user.is_authenticated:
        return redirect(url_for("main.garage"))

    login_form = login_form or LoginForm()
    registration_form = registration_form or RegistrationForm()

    return render_template("index.html", login_form=login_form, registration_form=registration_form,
                           modal_state=modal_state)


@main_bp.route('/register', methods=['POST'])
def register():
    registration_form = RegistrationForm()
    if not registration_form.validate_on_submit():
        return index(registration_form=registration_form, modal_state=2)
    registration_data = {
        'email': registration_form.email.data.lower(),
        'username': registration_form.username.data.lower(),
        'password': generate_password_hash(registration_form.password.data, 'pbkdf2:sha256', salt_length=16)
    }
    new_user = save_to_db(Users, registration_data)
    if new_user:
        login_user(new_user)
        return redirect(url_for('main.garage'))
    else:
        return index(modal_state=2)


@main_bp.route("/login", methods=['POST'])
def login():
    login_form = LoginForm()
    if not login_form.validate_on_submit():
        return index(login_form=login_form, modal_state=1)
    identifier = login_form.email_username.data.lower()
    password = login_form.password.data
    user = db.session.execute(
        db.Select(Users).where(or_(Users.username == identifier, Users.email == identifier))).scalar()
    if not check_password_hash(user.password, password):
        flash("Incorrect Password")
        return index(modal_state=1)
    login_user(user)
    return redirect(url_for('main.garage'))


@login_required
@main_bp.route("/garage", methods=['GET'])
def garage(add_vehicle_form=None, edit_vehicle_form=None, vehicles=None, modal_state=0):
    add_vehicle_form = add_vehicle_form or AddVehicleForm()
    edit_vehicle_form = edit_vehicle_form or EditVehicleForm()
    vehicles = vehicles or current_user.vehicles

    return render_template("garage.html", edit_vehicle_form=edit_vehicle_form,
                           add_vehicle_form=add_vehicle_form,
                           vehicles=vehicles, modal_state=modal_state)


@main_bp.route("/garage/search", methods=['POST'])
def vehicle_search():
    vehicle_model = request.form.get("vehicle_model")
    vehicles = [vehicle for vehicle in current_user.vehicles if vehicle.model == vehicle_model]
    if len(vehicles) < 1:
        flash(f"No vehicle found under {vehicle_model}")
        return redirect(url_for('main.garage'))
    return garage(vehicles=vehicles)


@login_required
@main_bp.route('/add-vehicle', methods=['POST'])
def add_vehicle():
    add_vehicle_form = AddVehicleForm()
    if not add_vehicle_form.validate_on_submit():
        return garage(add_vehicle_form=add_vehicle_form)
    picture_file = add_vehicle_form.picture.data
    picture_id = None
    if picture_file:
        picture_blob = file_to_blob(picture_file)
        add_picture_data = {'picture': picture_blob}
        picture = save_to_db(Pictures, add_picture_data)
        picture_id = picture.id
    add_vehicle_data = {'year': add_vehicle_form.year.data, 'make': add_vehicle_form.make.data,
                        'model': add_vehicle_form.model.data, 'mileage': add_vehicle_form.mileage.data,
                        'picture_id': picture_id, 'owner_id': current_user.id}
    vehicle = save_to_db(Vehicles, add_vehicle_data)
    if not vehicle:
        flash("Vehicle failed to save", "error")
        return garage()
    flash(f"{vehicle.model} successfully stored in garage")
    return redirect(url_for('main.garage'))


@login_required
@main_bp.route("/edit-vehicle", methods=['POST'])
def edit_vehicle():
    edit_vehicle_form = EditVehicleForm()
    if not edit_vehicle_form.validate_on_submit():
        return garage(edit_vehicle_form=edit_vehicle_form, modal_state=2)
    vehicle_id = request.form.get("vehicle_id")
    vehicle = retrieve_from_db(Vehicles, vehicle_id)
    if not vehicle:
        flash("Failure to find vehicle in database")
        return redirect(url_for('main.garage'))
    vehicle_data = {col_name: col_value.data for col_name, col_value in edit_vehicle_form._fields.items() if
                    not is_empty_field(col_value)}
    if 'picture' in vehicle_data:
        new_picture = file_to_blob(vehicle_data['picture'])
        picture_data = {'picture': new_picture}
        update_record(Pictures, vehicle.picture, picture_data)
    update_record(Vehicles, vehicle, vehicle_data)
    flash(f"{vehicle.model} successfully updated")
    return redirect(url_for('main.garage'))


@login_required
@main_bp.route("/services/<vehicle_id>", methods=["GET"])
def service_viewer(vehicle_id, add_service_form=None, modal_state=0):
    vehicle = db.session.execute(db.Select(Vehicles).where(
        and_(
            Vehicles.owner_id == current_user.id,
            Vehicles.id == vehicle_id)
    )).scalar()
    if not vehicle:
        flash("You are not authorized to view this vehicle's records", "error")
        return redirect(url_for('main.garage'))
    services = db.session.execute(db.Select(Services).where(
        and_(Services.owner_id == current_user.id,
             Services.vehicle_id == vehicle.id)
    )).scalars()

    add_service_form = add_service_form or AddServiceForm()

    return render_template("services.html", vehicle=vehicle, services=services, add_service_form=add_service_form,
                           modal_state=modal_state)


@main_bp.route("/add-service", methods=["POST"])
def add_service():
    add_service_form = AddServiceForm()
    vehicle_id = request.form.get('vehicle-id')
    if not add_service_form.validate_on_submit():
        return service_viewer(vehicle_id=vehicle_id, add_service_form=add_service_form, modal_state=1)

    picture_file = add_service_form.picture.data
    picture_id = None
    if picture_file:
        picture_blob = file_to_blob(picture_file)
        add_picture_data = {'picture': picture_blob}
        picture = save_to_db(Pictures, add_picture_data)
        picture_id = picture.id

    story = sanitize_html(add_service_form.story.data)
    add_service_data = {"owner_id": current_user.id, "vehicle_id": vehicle_id,
                        "date": add_service_form.date.data, "mileage": add_service_form.mileage.data,
                        "service": add_service_form.service.data, "story": story,
                        "picture_id": picture_id}
    service = save_to_db(Services, add_service_data)

    if not service:
        flash("Service failed to save", "error")
        return service_viewer(add_service_form=add_service_form, vehicle_id=vehicle_id)

    flash(f"{service.service} successfully stored in services")
    return redirect(url_for("main.service_viewer", vehicle_id=vehicle_id))


@login_required
@main_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("main.index"))


"""------------------------------------ RESTful api endpoints below--------------------------------------------------"""


@api_bp.route("/get-image/")
def get_image():
    """Fetches picture from database associated with id | Returns picture or placeholder picture if non existent"""
    # get picture id from url, retrieve picture object
    # extract picture col (Binary Data)
    # use bytes_io tool to construct BytesIO object
    # send file
    picture_id = request.args.get("picture_id")
    blob = Pictures.query.filter(Pictures.id == picture_id).scalar()
    if blob:
        return send_file(blob_to_file(blob.picture), mimetype="image/jpeg")
    else:
        return send_file("./static/placeholder_vehicle_image.png")


@login_required
@api_bp.route("/get-data", methods=['POST'])
def get_data():
    """data retrieval API
     request requirements:  BODY -> table: database table | id: database row primary key | columns: columns needed
     response: 200: json bundled data from database | 401: unauthorized data retrieval attempt"""
    req_body = request.get_json()
    db_id = req_body['id']
    table = req_body['table']
    cols = req_body['columns']

    # validates correct user attempting to access data then returns whole row as dictionary
    db_data = validate_data_request(current_user.id, db_id, table)

    if db_data:
        # packages requested data only from row into dict then returns it as json
        packaged_data = {}
        for col in cols:
            packaged_data[col] = getattr(db_data, col)
        return jsonify(packaged_data), 200
    else:
        # validation failed unauthorized access attempted
        return jsonify({"error": "Not authorized"}), 401


@login_required
@api_bp.route("/delete", methods=['POST'])
def delete():
    """Delete database row API
    request requirements: BODY -> table: database table | id: database row primary key
     response: 200: successful deletion | 401: unauthorized deletion attempt"""
    req_body = request.get_json()
    delete_id = req_body['id']
    table = req_body['table']

    to_delete = validate_delete_request(current_user.id, delete_id, table)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        return "", 200
    else:
        return jsonify({"error": 'Not authorized'}), 401
