from flask import Blueprint, render_template, redirect, request, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from .extensions import db, and_, or_, func
from .helpers import validate_delete_request, validate_data_request, sanitize_html
from .models import Vehicles, Users, Services, Pictures
from .forms import LoginForm, RegistrationForm, AddVehicleForm, EditVehicleForm, AddServiceForm

main_bp = Blueprint("main", __name__, template_folder="../templates")

""" TODOS

Immediate future 

1) make the date automatically input todays date when adding service if none is added
2) add label for date in add service form
3) allow users to input mileage in any form, IE with , or adding miles/ hours at end?
4) fix margin hack to get services and vehicles to display correctly and look nicely on mobile

Further future
1) add tag system to services to label as oil change , regular maintenance ect.. and also add pictures for each tag
2) search through vehicles and services feature
3) api for manufactures specified services to display service recommendations
4) add next recommended oil change date at top of services and on vehicle card
5) email user periodically recommending services for their vehicles

"""


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.garage"))
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if request.method == "POST":
        if 'login' in request.form:
            if login_form.validate_on_submit():
                user = Users.query.filter(
                    (func.lower(Users.username) == func.lower(login_form.email_username.data)) |
                    (func.lower(Users.email) == func.lower(login_form.email_username.data))
                ).first()
                if user and check_password_hash(user.password, login_form.password.data):
                    login_user(user)
                    return redirect(url_for("main.garage"))
            else:
                return render_template("index.html", login_form=login_form,
                                       registration_form=registration_form, modal_state=1)
        if 'register' in request.form:
            if registration_form.validate_on_submit():
                password = generate_password_hash(registration_form.password.data, method='pbkdf2:sha256',
                                                  salt_length=8)
                new_user = Users(email=registration_form.email.data, username=registration_form.username.data,
                                 password=password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("main.garage"))
            else:
                return render_template("index.html", login_form=login_form,
                                       registration_form=registration_form, modal_state=2)

    return render_template("index.html", login_form=login_form, registration_form=registration_form)


@login_required
@main_bp.route("/garage", methods=['GET', 'POST'])
def garage():
    vehicles = current_user.vehicles
    vehicle_model = request.form.get("vehicle_model")
    if vehicle_model:
        vehicles = [vehicle for vehicle in current_user.vehicles if vehicle.model == vehicle_model]
        if len(vehicles) < 1:
            flash(f"No vehicle found under {vehicle_model}")
            vehicles = current_user.vehicles

    add_vehicle_form = AddVehicleForm()
    edit_vehicle_form = EditVehicleForm()
    if request.method == "POST":
        if 'add' in request.form:
            if add_vehicle_form.validate_on_submit():
                picture = Pictures(picture=add_vehicle_form.picture.data.read())
                db.session.add(picture)
                db.session.commit()
                new_vehicle = Vehicles(owner_id=current_user.id, year=add_vehicle_form.year.data,
                                       make=add_vehicle_form.make.data,
                                       model=add_vehicle_form.model.data, mileage=add_vehicle_form.mileage.data,
                                       picture=picture.id)

                db.session.add(new_vehicle)
                db.session.commit()
                flash("Your new vehicle has been added to the garage", "success")
                return redirect(url_for("main.garage"))
            else:
                return redirect(url_for("main.garage", modal_state=1))
        if 'edit' in request.form:
            if edit_vehicle_form.validate_on_submit():
                vehicle = db.session.execute(db.Select(Vehicles).where(
                    Vehicles.id == int(request.form.get("vehicle_id")))).scalar()
                vehicle_attrs = ['year', 'make', 'model', 'mileage', 'picture']
                print(request.files)
                for attr in vehicle_attrs:

                    if attr in request.form or attr in request.files:
                        if attr == 'picture':
                            picture = db.session.execute(
                                db.Select(Pictures).where(Pictures.id == vehicle.picture)).scalar()
                            setattr(picture, attr, request.files[attr].read())

                        else:
                            setattr(vehicle, attr, request.form[attr])

                db.session.commit()
                flash(f"Successfully edited {vehicle.model}")
                return redirect(url_for("main.garage"))
    return render_template("garage.html", edit_vehicle_form=edit_vehicle_form, add_vehicle_form=add_vehicle_form,
                           vehicles=vehicles)


@login_required
@main_bp.route("/services/<vehicle_model>", methods=["GET", "POST"])
def service_viewer(vehicle_model):
    vehicle = db.session.execute(db.Select(Vehicles).where(
        and_(
            Vehicles.owner_id == current_user.id,
            Vehicles.model == vehicle_model)
    )).scalar()

    prior_services = db.session.execute(db.Select(Services).where(
        and_(Services.owner_id == current_user.id,
             Services.vehicle_id == vehicle.id)
    )).scalars()
    add_service_form = AddServiceForm()
    if request.method == "POST":
        if 'add' in request.form:
            if add_service_form.validate_on_submit():
                if add_service_form.picture:
                    picture = Pictures(picture=add_service_form.picture.data.read())
                    db.session.add(picture)
                story = sanitize_html(add_service_form.story.data)
                service = Services(vehicle_id=vehicle.id, owner_id=current_user.id, date=add_service_form.date.data,
                                   mileage=add_service_form.mileage.data,
                                   service=add_service_form.title.data, story=story)
                if picture:
                    service.picture = picture.id
                db.session.add(service)
                db.session.commit()

                return redirect(url_for("main.service_viewer", vehicle_model=vehicle.model, vehicle=vehicle))
            else:
                for error in add_service_form.errors.values():
                    flash(error)
                return redirect(url_for("main.service_viewer", vehicle_model=vehicle.model, vehicle=vehicle))
    return render_template("services.html", vehicle=vehicle, services=prior_services, add_service_form=add_service_form)


@main_bp.route("/get-image/")
def get_image():
    """Fetches picture from database associated with id | Returns picture or placeholder picture if non existent"""
    # get picture id from url, retrieve picture object
    # extract picture col (Binary Data)
    # use bytes_io tool to construct BytesIO object
    # send file
    picture_id = request.args.get("picture_id")
    blob = Pictures.query.filter(Pictures.id == picture_id).scalar()
    if blob.picture:
        bytes_io = BytesIO(blob.picture)
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype="image/jpg")
    else:
        return send_file("./static/placeholder_vehicle_image.png")


@login_required
@main_bp.route("/get-data", methods=['POST'])
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
@main_bp.route("/delete", methods=['POST'])
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



@login_required
@main_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("main.index"))
