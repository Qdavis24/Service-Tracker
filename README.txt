Hi all, I am a new computer science student and I came from an automotive background (worked as a tech in a Toyota dealership for 3 years). I am working on a web app that will store vehicles and services performed on them. The goal is to have one place you can access via computer or phone and keep track of your services performed like oil changes for instance. I was posting here to get some constructive criticism or feedback on the app. If you would like to check it out I have links to the repo and live site included in post.. Any input is welcome!
LIVE SITE: https://service-tracker.onrender.com/
REPO: https://github.com/Qdavis24/Service-Tracker/tree/main
TOOLS:
alembic==1.13.1
bleach==6.1.0
blinker==1.7.0
click==8.1.7
colorama==0.4.6
dnspython==2.6.1
email_validator==2.1.1
Flask==3.0.3
Flask-CKEditor==1.0.0
Flask-Login==0.6.3
Flask-Migrate==4.0.7
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
greenlet==3.0.3
idna==3.7
itsdangerous==2.2.0
Jinja2==3.1.3
jsonify==0.5
Mako==1.3.3
MarkupSafe==2.1.5
python-dotenv==1.0.1
six==1.16.0
SQLAlchemy==2.0.29
typing_extensions==4.11.0
webencodings==0.5.1
Werkzeug==3.0.2
WTForms==3.1.2
gunicorn==20.1.0
psycopg2-binary==2.9.3
TAILWIND CSS





TECHNICAL DETAILS:
I have chosen to use application factory design pattern for this project.
app
    app/static
        static/css
            garage.jpg
            wrenches.jpg
            wrenches.png

app/templates
app/templates/base.html
app/templates/garage.html
app/templates/index.html
app/templates/services.html

app/__init__.py
app/config.py
app/extensions.py
app/forms.py
app/models.py
app/run.py
app/views.py
 The general flow of the website is as follows. Index page contains two forms using Flask_WTF forms, one for login and one for registry. I use modal divs in the html and some javascript to change their display from none to flex to allow them to appear on screen when the appropriate button is clicked. The forms are then sent back to the server when submitted after some client side validation. once the forms are received server side the go through a second validation step. If they are validated then a user is either added to the database, using flask-sqlalchemy with SQL being the core db technology. If a user logs in the email is validated client side, then the form is sent to server and the email is validated once again as well as the password. The passwords are hashed and salted during registry and during authentication the passwords are checked by hashing the clear text and comparing to stored hash. 
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
For user auth I have chosen to use flask login and login manager to keep track of logged in users. Once the user is logged in they are presented with the "garage" page where a user can add or edit vehicles, again using flask_WTF forms. One feature I wanted to add was storing pictures. I accomplished this by creating a table in my database that stores BLOB data. I would recieve a picture via the form and then convert it to blob and store. When I wanted to retreive a picture I would use a view as an api and call upon it inside of the html by adding the api call to the image source with provided id data in the template. 
@main_bp.route("/get-image/<int:picture_id>")
def get_image(picture_id):
    # get picture id from url, retrieve picture object
    # extract picture col (Binary Data)
    # use bytes_io tool to construct BytesIO object
    # send file
    blob = Pictures.query.filter(Pictures.id == picture_id).first_or_404()
    blob = blob.picture
    bytes_io = BytesIO(blob)
    bytes_io.seek(0)
    return send_file(bytes_io, mimetype="image/jpg")

SIDE NOTE: if someone is looking to contribute to the project I have added some todos In the views module
