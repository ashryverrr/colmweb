from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from functools import wraps
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import InputRequired, Email
from flask_moment import Moment

app = Flask(__name__)
app.debug = True
# Set Moments to Global
moment = Moment(app)

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'colmweb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#Initialize SQL connection
mysql =  MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor() 
    cur.execute("SELECT id, title, body, author, created_at FROM blog LIMIT 6 ")
    blogs = cur.fetchall()
    
    return render_template('home.html', blogs = blogs)

###### REGISTER FORM ########
class RegisterForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=50)])
    lastName = StringField('Last Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=30)])
    email = StringField('Email', [validators.Length(min=6, max=50), Email("This field requires a valid email address")])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match.')        
        ])
    confirm = PasswordField('Confirm Password')

###### REGISTER ########
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        firstName = form.firstName.data
        lastName = form.lastName.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        accountType = "admin"
        # OPEN SQL CONNECTION
        cur = mysql.connection.cursor()
        # CHECK IF USERNAME OR PASSWORD ALREADY EXISTS
        result = cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email) ) 
        if result > 0:
            flash("Username or email is already used.", 'danger')
        else:                      
            # RUN QUERY
            cur.execute("INSERT INTO users (email, username, firstName, lastName, password, accountType) VALUES (%s, %s, %s, %s, %s, %s)", (email, username, firstName, lastName, password, accountType ))
            # SAVE TO DATABASE
            mysql.connection.commit()        
            cur.close
            flash("You have successfully registered. You can now login to the account.", 'success')
            return redirect(url_for('login'))
    else:        
        return render_template('register.html', form=form)


@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/academics')
def academics():
    return render_template('academics.html')

@app.route('/basic-education')
def basic_education():
    return render_template('basic-education.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

# FOR ADMINISTRATOR PAGE


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            #GET PASSWORD HASH
            data = cur.fetchone()
            password = data['password']
            firstName = data['firstName']
            lastName = data['lastName']
            #VALIDATE PASSWORD
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['fullName'] = firstName + ' ' + lastName
                
                
                flash("Your are now logged in.", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Password is incorrect.", 'danger')
            # CLOSE DB CONNECTION
            cur.close()
        else:
            flash("Username is incorrect.", 'danger')
    return render_template('login.html')

class BlogForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    body = TextAreaField('Body', [validators.Length(min=10)])
  
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = BlogForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data
        author = 1
        # OPEN SQL CONNECTION
        cur = mysql.connection.cursor()     
               
        cur.execute("INSERT INTO blog (title, body, author) VALUES (%s, %s, %s)", (title, body, author ))
        # SAVE TO DATABASE
        mysql.connection.commit()        
        cur.close
        flash("Blog post was successful.", 'success')
        return redirect(url_for('dashboard'))
    else:        
        return render_template('admin/dashboard.html', form=form)

@app.route('/blog')
def blog():
    cur = mysql.connection.cursor() 
    cur.execute("SELECT id, title, body, author, created_at FROM blog ")
    blogs = cur.fetchall()
    
    return render_template('admin/blog.html', blogs = blogs)
    

@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out.", 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key='secret1235'
    app.run()
    