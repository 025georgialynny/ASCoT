


from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    username= StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=10)])

class RegisterationForm(FlaskForm):
    role= SelectField(label = "role", choices = [(role, role) for role in ["admin", "user"]])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    firstname = StringField('First Name', validators=[InputRequired(), Length(min=2, max=15)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=15)])

class MgmtForm(FlaskForm):
    role= SelectField(label = "role", choices = [(role, role) for role in ["admin", "user"]])
    oldusername = HiddenField('oldusername')
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    firstname = StringField('First Name', validators=[InputRequired(), Length(min=2, max=15)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=15)])
    password = PasswordField('New Password', validators=[EqualTo("confpassword", message='Passwords must match')])
    confpassword = PasswordField('Confirm Password')


class PasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=4, max=15), EqualTo("confpassword", message='Passwords must match')])
    confpassword = PasswordField('Confirm Password')

class AllUserForm(FlaskForm):
    title=StringField("title")
    users= FieldList(FormField(MgmtForm))


class NewPrimer(FlaskForm):
    gene = StringField("Gene", validators = [InputRequired()])
    exon = StringField("Exon")
    rsid = StringField("rsID")
    pnum = StringField("Primer Num (p#)")
    diplotype = StringField("Diplotype")
    m13 = BooleanField("M13")