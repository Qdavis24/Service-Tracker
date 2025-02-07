from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, ValidationError, FileField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_ckeditor import CKEditorField

# my modules
from .extensions import func
from .models import Users


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email("Invalid email address")],
        render_kw={
            'placeholder': 'Email',
            "class": "p-2", }
    )

    username = StringField('Username',
                           validators=[DataRequired()],
                           render_kw={
                               'placeholder': 'Username',
                               "class": "p-2", }
                           )

    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Length(min=6, message="Password must be 6 characters long"),
                             ],
                             render_kw={"placeholder": "Password",
                                        "class": "p-2"})

    confirm_password = PasswordField('Confirm_Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message="Passwords must match")],
                                     render_kw={
                                         'placeholder': 'Confirm Password',
                                         "class": "p-2",
                                     },
                                     )

    submit = SubmitField('Submit')

    def validate_username(self, field):
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email_username = StringField('Email/Username',
                                 validators=[DataRequired()],
                                 render_kw={
                                     'placeholder': 'Email/Username',
                                     "class": "p-2",
                                 }
                                 )
    password = PasswordField('Password',
                             validators=[DataRequired()],
                             render_kw={
                                 'placeholder': 'Password',
                                 "class": "p-2",
                             }
                             )
    submit = SubmitField('Submit')

    def validate_email_username(self, field):
        if not Users.query.filter(
                (func.lower(Users.email) == func.lower(field.data)) | (
                        func.lower(Users.username) == func.lower(field.data))
        ).first():
            raise ValidationError('Email or Username does not exist')


class AddVehicleForm(FlaskForm):
    year = StringField('Year', validators=[DataRequired()],
                       render_kw={

                           'placeholder': 'Year',
                           'id': 'add_year',
                       }
                       )
    make = StringField('Make', validators=[DataRequired()],
                       render_kw={

                           'placeholder': 'Make',
                           'id': 'add_make',
                       }
                       )
    model = StringField('Model', validators=[DataRequired()],
                        render_kw={

                            'placeholder': 'Model',
                            'id': 'add_model',
                        }
                        )
    mileage = StringField('Mileage',
                          render_kw={

                              'placeholder': 'Mileage',
                              'id': 'add_mileage',
                          }
                          )
    picture = FileField('Vehicle Picture',
                        render_kw={
                            'placeholder': 'Picture',
                        }
                        )
    submit = SubmitField('Submit')


class EditVehicleForm(FlaskForm):
    year = StringField('Year', validators=[DataRequired()],
                       render_kw={
                           'placeholder': 'Year',
                           'id': "year"
                       }
                       )
    make = StringField('Make', validators=[DataRequired()],
                       render_kw={
                           'placeholder': 'Make',
                           'id': "make"
                       }
                       )
    model = StringField('Model', validators=[DataRequired()],
                        render_kw={
                            'placeholder': 'Model',
                            "id": "model"
                        }
                        )
    mileage = StringField('Mileage',
                          render_kw={
                              'placeholder': 'Mileage',
                              'id': "mileage"
                          }
                          )
    picture = FileField('Vehicle Picture',
                        render_kw={
                            'placeholder': 'Picture',
                        }
                        )
    submit = SubmitField('Submit')


class AddServiceForm(FlaskForm):
    date = DateField('Date of Service', validators=[DataRequired()],
                     render_kw={
                         'id': "add_date"
                     }
                     )
    mileage = StringField('Mileage', validators=[DataRequired()],
                          render_kw={
                              'placeholder': 'Mileage',
                              'id': "add_mileage"
                          }
                          )
    service = StringField('Service Preformed', validators=[DataRequired()],
                          render_kw={
                              'placeholder': 'Title of service',
                              'id': "add_service"
                          }
                          )
    story = CKEditorField('Service Description', validators=[DataRequired()],
                          render_kw={
                              'id': "add_story"
                          }
                          )
    picture = FileField('Vehicle Picture')
    submit = SubmitField('Submit')


class EditServiceForm(FlaskForm):
    date = DateField('Date of Service', validators=[DataRequired()],
                     render_kw={
                         'id': "date"
                     }
                     )
    mileage = StringField('Mileage', validators=[DataRequired()],
                          render_kw={
                              'placeholder': 'Mileage',
                              'id': "mileage"
                          }
                          )
    service = StringField('Service Preformed', validators=[DataRequired()],
                          render_kw={
                              'placeholder': 'Title of service',
                              'id': "service"
                          }
                          )
    story = CKEditorField('Service Description', validators=[DataRequired()],
                          render_kw={
                              'id': "story"
                          }
                          )
    picture = FileField('Vehicle Picture')
    submit = SubmitField('Submit')
