from flask_wtf import FlaskForm
from sqlalchemy.testing.pickleable import User
from wtforms import StringField, SubmitField, HiddenField, ValidationError, FileField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_ckeditor import CKEditor, CKEditorField

# my modules
from .extensions import db
from .models import Users


class RegistrationForm(FlaskForm):
    register = HiddenField()
    email = StringField(
        'Email',
        validators=[DataRequired(), Email("Invalid email address")],
        render_kw={
            'class': "mt-2 p-3 border rounded w-full",
            'placeholder': 'Email'
        }
    )

    username = StringField('Username',
                           validators=[DataRequired()],
                           render_kw={
                               'class': "mt-2 p-3 border rounded w-full",
                               'placeholder': 'Username'
                           }
                           )

    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Length(min=6, message="Password must be 6 characters long"),
                                 EqualTo('confirm_password', message="Passwords must match")
                             ],
                             render_kw={
                                 'class': "mt-2 p-3 border rounded w-full", 'placeholder': 'Password'
                             }
                             )

    confirm_password = PasswordField('Confirm_Password',
                                     validators=[DataRequired()],
                                     render_kw={
                                         'class': "mt-2 p-3 border rounded w-full",
                                         'placeholder': 'Confirm Password'
                                     }
                                     )

    submit = SubmitField('Submit',
                         render_kw={
                             'class': 'mt-4 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full'
                         }
                         )

    def validate_username(self, field):
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    login = HiddenField()
    email_username = StringField('Email/Username',
                                 validators=[DataRequired(),
                                             Email("Invalid email address")],
                                 render_kw={
                                     'class': "mt-2 p-3 border rounded w-full",
                                     'placeholder': 'Email/Username'
                                 }
                                 )
    password = PasswordField('Password',
                             validators=[DataRequired()],
                             render_kw={
                                 'class': "mt-2 p-3 border rounded w-full",
                                 'placeholder': 'Password'
                             }
                             )
    submit = SubmitField('Submit',
                         render_kw={
                             'class': 'mt-4 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full'
                         }
                         )

    def validate_email_username(self, field):
        if not Users.query.filter((Users.email == field.data) | (Users.username == field.data)).first():
            raise ValidationError('Email or Username does not exist')


class AddVehicleForm(FlaskForm):
    add = HiddenField()
    year = StringField('Year', validators=[DataRequired()],
                       render_kw={
                           'class': "mt-2 p-3 border rounded w-full",
                           'placeholder': 'Year'
                       }
                       )
    make = StringField('Make', validators=[DataRequired()],
                       render_kw={
                           'class': "mt-2 p-3 border rounded w-full",
                           'placeholder': 'Make'
                       }
                       )
    model = StringField('Model', validators=[DataRequired()],
                        render_kw={
                            'class': "mt-2 p-3 border rounded w-full",
                            'placeholder': 'Model'
                        }
                        )
    mileage = StringField('Mileage',
                          render_kw={
                              'class': "mt-2 p-3 border rounded w-full",
                              'placeholder': 'Mileage'
                          }
                          )
    picture = FileField('Vehicle Picture',
                        render_kw={
                            'class': "mt-2 p-3 border rounded w-full",
                            'placeholder': 'Picture'
                        }
                        )
    submit = SubmitField('Submit',
                         render_kw={
                             'class': 'mt-4 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full'
                         }
                         )


class EditVehicleForm(FlaskForm):
    edit = HiddenField()
    year = StringField('Year', validators=[DataRequired()],
                       render_kw={
                           'class': "mt-2 p-3 border rounded w-full",
                           'placeholder': 'Year',
                           'id': "y"
                       }
                       )
    make = StringField('Make', validators=[DataRequired()],
                       render_kw={
                           'class': "mt-2 p-3 border rounded w-full",
                           'placeholder': 'Make',
                           'id': "mke"
                       }
                       )
    model = StringField('Model', validators=[DataRequired()],
                        render_kw={
                            'class': "mt-2 p-3 border rounded w-full",
                            'placeholder': 'Model',
                            "id": "mdl"
                        }
                        )
    mileage = StringField('Mileage',
                          render_kw={
                              'class': "mt-2 p-3 border rounded w-full",
                              'placeholder': 'Mileage',
                              'id': "mil"
                          }
                          )
    picture = FileField('Vehicle Picture',
                        render_kw={
                            'class': "mt-2 p-3 border rounded w-full",
                            'placeholder': 'Picture'
                        }
                        )
    submit = SubmitField('Submit',
                         render_kw={
                             'class': 'mt-4 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full'
                         }
                         )


class AddServiceForm(FlaskForm):
    add = HiddenField()
    date = DateField('Date of Service', render_kw={"class": "mt-2 p-3 border rounded w-full", "placeholder": "Date of Service"})
    mileage = StringField('Mileage', render_kw={"class": "mt-2 p-3 border rounded w-full", "placeholder": "Mileage"})
    title = StringField('Service Preformed', render_kw={"class": "mt-2 p-3 border rounded w-full", "placeholder": "Service"})
    story = CKEditorField('Service Description', render_kw={"placeholder": "Service Description"})
    picture = FileField('Vehicle Picture',
                        render_kw={
                            'class': "mt-2 p-3 border rounded w-full",
                            'placeholder': 'Picture'
                        }
                        )
    submit = SubmitField('Submit', render_kw={
        'class': 'mt-4 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full'
    }
                         )
