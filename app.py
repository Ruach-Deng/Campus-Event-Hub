
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


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'app.db')
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    events = db.relationship('Event', backref='author', lazy=True)
    rsvps = db.relationship('RSVP', backref='user', lazy=True)
    
    
    # Methods to set and check password
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Define a user loader function to load a user from the database based on their user ID
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the Event model
class Event(db.Model):
    # Defining all the class variables
    id = db.Column(db.Integer, primary_key=True)
    title: so.Mapped[str] = so.mapped_column(index=True, default="No title")
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=datetime.now)
    location: so.Mapped[str] = so.mapped_column(index=True, default="No Location")
    description: so.Mapped[str] = so.mapped_column(index=True, default="No Description")
    category: so.Mapped[str] = so.mapped_column(index=True, default="No Category")
    created_at:so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    user_id :so.Mapped[int] = so.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rsvps = db.relationship('RSVP', backref='event', lazy=True, cascade='all, delete-orphan')    

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


#Initialize the database and create the user table
with app.app_context():
    db.create_all()


@app.route("/")
def home():
   # Get upcoming events (limit to 3)
    upcoming_events = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date).limit(3).all()
    return render_template('home.html', upcoming_events=upcoming_events)

# Route to display all events with optional filtering by category and search term
@app.route('/events', methods=['GET', 'POST'])
def event_list():
    category = request.args.get('category')
    search = request.args.get('search')
    
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
    
    events = query.order_by(Event.date.desc()).all()
    return render_template('events.html', events=events, category=category, search=search)

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
        
        # Validation
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
    
    # Check if already RSVP'd
    existing_rsvp = RSVP.query.filter_by(user_id=session['user_id'], event_id=event_id).first()
    
    if existing_rsvp:
        flash('You have already RSVP\'d to this event', 'info')
    else:
        new_rsvp = RSVP(user_id=session['user_id'], event_id=event_id)
        db.session.add(new_rsvp)
        db.session.commit()
        flash('RSVP successful!', 'success')
    
    return redirect(url_for('event_list'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user) 
            session['user_id'] = user.id
            session['user_email'] = user.email
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
        
        # Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))
        
if __name__ == '__main__':
    app.run(debug=True)





