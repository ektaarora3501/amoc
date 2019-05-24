
#from main.models import data_user
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,ValidationError,validators,PasswordField,SubmitField
from wtforms.validators import DataRequired,EqualTo,Length,Email
#from main.models import data_user


class Regis_form(FlaskForm):
	username=StringField('USERNAME',validators=[DataRequired(),Length(min=4,max=20)])
	password=PasswordField('PASSWORD',validators=[DataRequired(),Length(min=5,max=9)])
	cnf_pass=PasswordField('CONFIRM PASSWORD',validators=[DataRequired(),EqualTo('password')])
	email=StringField("EMAIL",validators=[DataRequired(),Email()])
	submit=SubmitField('Sign Up')
               



class login_form(FlaskForm):
        username=StringField('USERNAME',validators=[DataRequired(),Length(min=4,max=20)])
        password=PasswordField('PASSWORD',validators=[DataRequired(),Length(min=5,max=9)])
        email=StringField("EMAIL",validators=[DataRequired(),Email()])
        submit=SubmitField('Sign In')
