from flask import render_template, flash, redirect, url_for, request
from app import db
from app.forms import RegistrationForm, LoginForm, ResourceForm
from app.models import User, Resource
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask import current_app as app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # Redirect to the next page if exists
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/resources')
def resources():
    resources = Resource.query.order_by(Resource.date_added.desc()).all()
    return render_template('resources.html', title='Resources', resources=resources)

@app.route('/add_resource', methods=['GET', 'POST'])
@login_required
def add_resource():
    form = ResourceForm()
    if form.validate_on_submit():
        resource = Resource(
            title=form.title.data,
            description=form.description.data,
            resource_type=form.resource_type.data,
            link=form.link.data
        )
        db.session.add(resource)
        db.session.commit()
        flash('New resource has been added!')
        return redirect(url_for('resources'))
    return render_template('add_resource.html', title='Add Resource', form=form)
