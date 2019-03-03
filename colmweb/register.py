from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import InputRequired, Email

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=30)])
    email = StringField('Email', [validators.Length(min=6, max=50), Email("This field requires a valid email address")])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match.')        
        ])
    confirm = PasswordField('Confirm Password')

def register():
    form = RegisterForm(request.form)
    if method.request == "POST":
        name = form.data.name
        username = form.data.username
        email = form.data.email
        password = form.data.password
    else:        
        return render_template('register.html')
