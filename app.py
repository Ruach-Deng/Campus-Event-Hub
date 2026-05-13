from flask import Flask, render_template, request, redirect, session, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_required, UserMixin, current_user, login_user, logout_user
from flask import flash
from flask import get_flashed_messages
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'app.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = (
    database_url
    or "sqlite:///" + os.path.join(basedir, 'app.db')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


# Define the User model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    events = db.relationship('Event', backref='author', lazy=True, cascade='all, delete-orphan')
    rsvps = db.relationship('RSVP', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(user_id):
    return  db.session.get(User, int(user_id))


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
    user_id: so.Mapped[int] = so.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rsvps = db.relationship('RSVP', backref='event', lazy=True, cascade='all, delete-orphan')


class RSVP(db.Model):
    __tablename__ = "rsvps"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Initialize the database
#with app.app_context():
 #   db.create_all()


@app.route("/")
def home():
    upcoming_events = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date).limit(6).all()
    return render_template('home.html', upcoming_events=upcoming_events)


# ── Event list with upcoming/past filter ──
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

    # NEW: filter by upcoming or past
    if tab == 'past':
        query = query.filter(Event.date < datetime.now())
        events = query.order_by(Event.date.desc()).all()
    else:
        query = query.filter(Event.date >= datetime.now())
        events = query.order_by(Event.date.asc()).all()

    return render_template('events.html', events=events, category=category, search=search, tab=tab)


# ── NEW: Event detail page ──
@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    user_rsvpd = False
    if 'user_id' in session:
        user_rsvpd = RSVP.query.filter_by(
            user_id=session['user_id'], event_id=event_id
        ).first() is not None
    return render_template('event_detail.html', event=event, user_rsvpd=user_rsvpd)


@app.route('/post-event', methods=['GET', 'POST'])
@login_required
def post_event():

    if 'user_id' not in session:
        flash('Please login to post an event', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        category = request.form.get('category')

        if not all([title, date_str, location, description, category]):
            flash('All fields are required', 'error')
            return redirect(url_for('post_event'))

        try:
            event_date = datetime.fromisoformat(date_str)
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('post_event'))

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


@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):

    if 'user_id' not in session:
        flash('Please login to edit events', 'error')
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)

    if event.user_id != session['user_id']:
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


@app.route('/event/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):

    if 'user_id' not in session:
        flash('Please login to delete events', 'error')
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)

    if event.user_id != session['user_id']:
        flash('You can only delete your own events', 'error')
        return redirect(url_for('event_list'))

    db.session.delete(event)
    db.session.commit()

    flash('Event deleted successfully!', 'success')
    return redirect(url_for('event_list'))


@app.route('/event/<int:event_id>/rsvp', methods=['POST'])
def rsvp_event(event_id):

    if 'user_id' not in session:
        flash('Please login to RSVP', 'error')
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)

    existing_rsvp = RSVP.query.filter_by(user_id=session['user_id'], event_id=event_id).first()

    if existing_rsvp:
        flash('You have already RSVP\'d to this event', 'info')
    else:
        new_rsvp = RSVP(user_id=session['user_id'], event_id=event_id)
        db.session.add(new_rsvp)
        db.session.commit()
        flash('RSVP successful!', 'success')

    return redirect(url_for('event_detail', event_id=event_id))


# ── NEW: Cancel RSVP ──
@app.route('/event/<int:event_id>/cancel-rsvp', methods=['POST'])
def cancel_rsvp(event_id):
    if 'user_id' not in session:
        flash('Please login to cancel RSVP', 'error')
        return redirect(url_for('login'))

    rsvp = RSVP.query.filter_by(user_id=session['user_id'], event_id=event_id).first()

    if rsvp:
        db.session.delete(rsvp)
        db.session.commit()
        flash('RSVP cancelled successfully', 'success')
    else:
        flash('No RSVP found to cancel', 'info')

    return redirect(url_for('event_detail', event_id=event_id))


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    user_events = Event.query.filter_by(user_id=user.id).order_by(Event.date).all()
    user_rsvps = RSVP.query.filter_by(user_id=user.id).all()
    total_rsvps = sum(len(e.rsvps) for e in user_events)
    upcoming_count = Event.query.filter(Event.date >= datetime.utcnow()).count()
    return render_template('dashboard.html',
        user_events=user_events, user_rsvps=user_rsvps,
        total_rsvps=total_rsvps, upcoming_count=upcoming_count)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        try:

            hashed_password = generate_password_hash(password)
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            print(e)

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()

    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))


@app.errorhandler(404)
def not_found(error):
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