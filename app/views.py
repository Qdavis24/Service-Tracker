from flask import Blueprint, render_template, redirect, request, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from .extensions import db, and_, or_
from .models import Vehicles, Users, Services, Pictures
from .forms import LoginForm, RegistrationForm, AddVehicleForm, EditVehicleForm, AddServiceForm

main_bp = Blueprint("main", __name__, template_folder="../templates")


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.garage"))
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if request.method == "POST":
        if 'login' in request.form:
            if login_form.validate_on_submit():
                user = Users.query.filter((Users.username == login_form.email_username.data) |
                                          (Users.email == login_form.email_username.data)).first()
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
                flash(f"Successfully updated {vehicle.make}")
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
    add_service_form = AddServiceForm()
    prior_services = db.session.execute(db.Select(Services).where(Services.owner_id == current_user.id)).scalars()
    if request.method == "POST":
        print("y")
        if 'add' in request.form:
            print("yy")
            if add_service_form.validate_on_submit():
                print('yyyy')
                picture = Pictures(picture=add_service_form.picture.data.read())
                db.session.add(picture)
                db.session.commit()
                service = Services(vehicle_id=vehicle.id, owner_id=current_user.id, date=add_service_form.date.data, mileage=add_service_form.mileage.data,
                                   service=add_service_form.title.data, story=add_service_form.story.data,
                                   picture=picture.id)
                db.session.add(service)
                db.session.commit()

                return redirect(url_for("main.service_viewer", vehicle_model=vehicle.model, vehicle=vehicle))
            else:
                for error in add_service_form.errors.values():
                    flash(error)
                return redirect(url_for("main.service_viewer", vehicle_model=vehicle.model, vehicle=vehicle))
    return render_template("services.html", vehicle=vehicle, services=prior_services, add_service_form=add_service_form)


@main_bp.route("/get-image/<int:picture_id>")
def get_image(picture_id):
    blob = Pictures.query.filter(Pictures.id == picture_id).first_or_404()
    blob = blob.picture
    bytes_io = BytesIO(blob)
    bytes_io.seek(0)
    return send_file(bytes_io, mimetype="image/jpg")


@main_bp.route("/get-vehicle-data/<int:vehicle_id>")
def get_vehicle_data(vehicle_id):
    print(vehicle_id)
    vehicle = Vehicles.query.filter(Vehicles.id == vehicle_id).first_or_404()
    needed_data = ["year", "make", "model", "mileage", "id"]
    vehicle_data = {col.name: str(getattr(vehicle, col.name)) for col in vehicle.__table__.columns if col.name in
                    needed_data}
    print(vehicle_data)
    return jsonify(vehicle_data)


@main_bp.route("/delete-vehicle/<int:vehicle_id>")
def delete_vehicle(vehicle_id):
    vehicle = Vehicles.query.filter(Vehicles.id == vehicle_id).first()
    db.session.delete(vehicle)
    db.session.commit()
    return redirect(url_for("main.garage"))
@main_bp.route("/delete-service/<int:service_id>")
def delete_service(service_id):
    service = Services.query.filter(Services.id == service_id).first()
    print(request.args.get("vehicle_model"))
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("main.service_viewer", vehicle_model=request.args.get("vehicle_model")))

@login_required
@main_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("main.index"))
