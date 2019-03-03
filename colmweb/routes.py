import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from colmweb.forms import RegistrationForm, LoginForm, PostForm
from colmweb.models import User, Post
from colmweb import app, db, bcrypt
from flask_login import login_user, current_user,logout_user, login_required


@app.route('/')
@app.route('/index')
def index():      
    return render_template('home.html')

###### REGISTER ########
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():   
       hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       user = User(username=form.username.data, email=form.email.data, password=hashed_password)
       db.session.add(user)
       db.session.commit()
       flash(f'Your account has been created. You are now able to login.', 'success')
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

@app.route("/login", methods=['GET', 'POST'])
def login():
   if current_user.is_authenticated:
       return redirect(url_for('dashboard'))
   form = LoginForm()
   if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user and bcrypt.check_password_hash(user.password, form.password.data):
           login_user(user, remember=form.remember.data)
           next_page = request.args.get('next')
           flash(f'Login successful.', 'success')
           return redirect(next_page) if next_page else redirect(url_for('login'))
       else:
           flash(f'Login unsuccessful. Please check email or password', 'danger')  
   return render_template('login.html', title='Login', form=form)

  
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = PostForm()
    if request.method == "POST" and form.validate():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash(f'Your post has been created.', 'success')
        return redirect(url_for('dashboard'))
    else:        
        return render_template('admin/dashboard.html', form=form)

@app.route('/blog')
def blog():    
    return render_template('admin/blog.html')
    

@app.route('/logout')
def logout():
    logout_user()
    flash(f'Logout successfully!', 'success') 
    return redirect(url_for('login'))