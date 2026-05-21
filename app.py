from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_required, UserMixin, current_user, login_user, logout_user
from flask import flash
from flask import get_flashed_messages
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from email_validator import validate_email, EmailNotValidError

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

csrf = CSRFProtect(app)

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.config['SESSION_REFRESH_EACH_REQUEST'] = True

app.config['SESSION_COOKIE_SECURE'] = os.environ.get('DATABASE_URL') is not None
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('DATABASE_URL') is not None
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = "Lax"


#set secret key from environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

basedir = os.path.abspath(os.path.dirname(__file__))

# configure database URL for Heroku Postgres
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Railway provides DATABASE_URL with postgres:// prefix
    # SQLAlchemy requires postgresql:// prefix
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.session_protection = "basic"
login.login_view = 'login'


# Define the User model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    events = db.relationship('Event', backref='author', lazy=True)
    rsvps = db.relationship('RSVP', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Define the Event model
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title: so.Mapped[str] = so.mapped_column(index=True, default="No title")
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=datetime.now)
    location: so.Mapped[str] = so.mapped_column(index=True, default="No Location")
    description: so.Mapped[str] = so.mapped_column(index=True, default="No Description")
    category: so.Mapped[str] = so.mapped_column(index=True, default="No Category")
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    user_id: so.Mapped[int] = so.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rsvps = db.relationship('RSVP', backref='event', lazy=True, cascade='all, delete-orphan')

# Define the RSVP model
class RSVP(db.Model):
    __tablename__ = "rsvps"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Initialize the database
with app.app_context():
    db.create_all()

# Home page with upcoming events
@app.route("/")
def home():
    upcoming_events = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date).limit(6).all()
    return render_template('home.html', upcoming_events=upcoming_events)


# Event list with upcoming/past filter 
@app.route('/events', methods=['GET', 'POST'])
def event_list():
    category = request.args.get('category')
    search = request.args.get('search')
    tab = request.args.get('tab', 'upcoming')  # NEW: upcoming or past

    query = Event.query

    if category:
        query = query.filter_by(category=category)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Event.title.like(search_term),
                Event.description.like(search_term),
                Event.location.like(search_term)
            )
        )

    # filter by upcoming or past
    if tab == 'past':
        query = query.filter(Event.date < datetime.now())
        events = query.order_by(Event.date.desc()).all()
    else:
        query = query.filter(Event.date >= datetime.now())
        events = query.order_by(Event.date.asc()).all()

    return render_template('events.html', events=events, category=category, search=search, tab=tab)

# event detail page with RSVP status 
@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    user_rsvpd = False

    if current_user.is_authenticated:
        user_rsvpd = RSVP.query.filter_by(
            user_id=current_user.id, event_id=event_id
        ).first() is not None

    # Pass user email for avatar
    user_email = current_user.email if current_user.is_authenticated else ""
    
    return render_template('event_detail.html', event=event, user_rsvpd=user_rsvpd )


# Post event route with ownership check
@app.route('/post-event', methods=['GET', 'POST'])
@login_required
def post_event():
   
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        date_str = request.form.get('date', '')
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()

        # check for empty fields
        if not all([title, date_str, location, description, category]):
            flash('All fields are required', 'error')
            return redirect(url_for('post_event'))
        
        # convert date
        try:
            event_date = datetime.fromisoformat(date_str)
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('post_event'))
        
        # Title validation
        #if len(title) < 3:
         #   flash("Title too short", "error")
          #  return redirect(url_for('post_event'))
        
        # Location validation
        if len(location) < 2:
            flash("Location too short", "error")
            return redirect(url_for('post_event'))
        
        # Allowed categories
        allowed_categories = ["Social","Academics","Sports","Clubs","Workshop"]

        if category not in allowed_categories:
            flash("Invalid category", "error")
            return redirect(url_for('post_event'))
        
        # Prevent past dates
        if event_date < datetime.now():
            flash("Event date cannot be in the past", "error")
            return redirect(url_for('post_event'))
        
         # Description limit
        if len(description) > 1000:
            flash("Description too long", "error")
            return redirect(url_for('post_event'))
        
        #create event
        new_event = Event(
            title=title,
            date=event_date,
            location=location,
            description=description,
            category=category,
            user_id=current_user.id
        )

        db.session.add(new_event)
        db.session.commit()

        flash('Event posted successfully!', 'success')
        return redirect(url_for('event_list'))

    return render_template('post_event.html')

# Edit event route with ownership check
@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):

    event = Event.query.get_or_404(event_id)

    if event.user_id != current_user.id:
        flash('You can only edit your own events', 'error')
        return redirect(url_for('event_list'))

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.date = datetime.fromisoformat(request.form.get('date'))
        event.location = request.form.get('location')
        event.description = request.form.get('description')
        event.category = request.form.get('category')

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event_list'))

    return render_template('edit_event.html', event=event)

# Delete event route with ownership check
@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    
    event = Event.query.get_or_404(event_id)

    if event.user_id != current_user.id:
        flash('You can only delete your own events', 'error')
        return redirect(url_for('event_list'))

    db.session.delete(event)
    db.session.commit()

    flash('Event deleted successfully!', 'success')
    return redirect(url_for('event_list'))

# RSVP route
@app.route('/event/<int:event_id>/rsvp', methods=['POST'])
@login_required
def rsvp_event(event_id):

    event = Event.query.get_or_404(event_id)

    existing_rsvp = RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first()

    if existing_rsvp:
        flash('You have already RSVP\'d to this event', 'info')
    else:
        new_rsvp = RSVP(user_id=current_user.id, event_id=event_id)
        db.session.add(new_rsvp)
        db.session.commit()
        flash('RSVP successful!', 'success')

    return redirect(url_for('event_detail', event_id=event_id))


# Cancel RSVP route
@app.route('/event/<int:event_id>/cancel-rsvp', methods=['POST'])
@login_required
def cancel_rsvp(event_id):
   
    rsvp = RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first()

    if rsvp:
        db.session.delete(rsvp)
        db.session.commit()
        flash('RSVP cancelled successfully', 'success')
    else:
        flash('No RSVP found to cancel', 'info')

    return redirect(url_for('event_detail', event_id=event_id))

# User dashboard with event and RSVP management
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(current_user.id)
    user_events = Event.query.filter_by(user_id=user.id).order_by(Event.date).all()
    user_rsvps = RSVP.query.filter_by(user_id=user.id).all()
    total_rsvps = sum(len(e.rsvps) for e in user_events)
    upcoming_count = Event.query.filter(Event.date >= datetime.utcnow()).count()
    return render_template('dashboard.html',
        user_events=user_events, user_rsvps=user_rsvps,
        total_rsvps=total_rsvps, upcoming_count=upcoming_count)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True, duration=timedelta(days=7))
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

# Registration route with validation 
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # check empty fields
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('register'))
        
        # validate email format
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash('Invalid email format', 'error')
            return redirect(url_for('register'))
        
        # check password length
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))
        
        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)

        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )