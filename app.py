# =========================
# IMPORTS
# =========================

from flask import Flask
from flask import render_template
from flask import url_for
from flask import flash
from flask import redirect
from flask import request

from forms import RegistrationForm
from forms import LoginForm

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user
)


# =========================
# POSTS
# =========================

posts = [
    {
        'author': 'Tech master',
        'title': 'first post',
        'content': 'no more google, gmail, tracking. use duckduckgo.com',
        'date_posted': '09 Sept 2026'
    },
    {
        'author': 'Ajaj',
        'title': 'second post',
        'content': 'no more youtube. use protonmail.com',
        'date_posted': '11 Sept 2026'
    }
]


# =========================
# FLASK APP
# =========================

app = Flask(__name__)


# =========================
# CONFIGURATION
# =========================

app.config['SECRET_KEY'] = 'your-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_blog.db'


# =========================
# DATABASE
# =========================

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)


# =========================
# LOGIN MANAGER
# =========================

login_manager = LoginManager(app)

login_manager.login_view = 'login'

login_manager.login_message_category = 'info'


# =========================
# USER MODEL
# =========================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    image_file = db.Column(
        db.String(20),
        nullable=False,
        default='default.jpg'
    )

    password = db.Column(
        db.String(60),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# =========================
# USER LOADER
# =========================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# =========================
# HOME
# =========================

@app.route('/')
@app.route('/home')
def index():

    return render_template(
        'index.html',
        posts=posts
    )


# =========================
# ABOUT
# =========================

@app.route('/about')
def about():

    return render_template(
        'about.html',
        title='About Us'
    )


# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode('utf-8')

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash(
            'User registered successfully!',
            'success'
        )

        return redirect(
            url_for('login')
        )

    return render_template(
        'register.html',
        title='Registration Page',
        form=form
    )


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            form.password.data
        ):

            login_user(
                user,
                remember=form.remember.data
            )

            next_page = request.args.get('next')

            flash(
                'Login successful!',
                'success'
            )

            if next_page:
                return redirect(next_page)

            return redirect(
                url_for('index')
            )

        else:

            flash(
                'Username or Password is incorrect!',
                'danger'
            )

    return render_template(
        'login.html',
        form=form,
        title='Login'
    )


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    logout_user()

    return redirect(
        url_for('index')
    )


# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(debug=True)