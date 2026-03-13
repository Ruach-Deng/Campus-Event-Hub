# 🎓 Campus Event Hub

Campus Event Hub is a full-stack web application built by a student group
as part of a web development capstone project. The goal was to create a
centralised platform where university students can discover what is
happening on campus, share their own events with the community, and
keep track of the activities they plan to attend.

The application is built entirely in Python using the Flask framework,
with a SQLite database managed through Flask-SQLAlchemy and HTML
templates powered by Jinja2. The front end uses Pico CSS as a base
with custom styling on top.

## 🚀 Live Demo

> Currently runs locally — deployment coming in second release candidate.

## ✅ Features in first release candidate

- User registration and login (session-based authentication)
- Post, edit, and delete campus events
- Browse all events with search and category filtering
- RSVP to events with live attendee count
- Personal user dashboard (stats, your events, your RSVPs, activity feed)
- Five event categories: Academics, Sports, Social, Clubs, Workshops

## 🛠️ Installation & Setup

### Requirements

- Python 3.9 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/Ruach-Deng/Campus-Event-Hub.git
cd campus-event-hub
```
### 2. Create a virtual environment
```bash
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

### 3. Install dependencies
```bash
pip install -r requirements.txt

### 4. Set up the database
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 5. Run the app
```bash
flask run
```

Then open your browser and go to: **http://127.0.0.1:5000**

## 📦 Dependencies (requirements.txt)

Make sure this file exists in your project root:
```
Flask
Flask-SQLAlchemy
Werkzeug
```

Generate it automatically by running:
```bash
pip freeze > requirements.txt
```

## 👤 How to Use

### Register & Log In
1. Click **Register** in the top navigation
2. Enter your email and a password
3. You will be redirected to the homepage — you are now logged in

### Post an Event
1. Click **Post Event** in the navigation bar
2. Fill in the title, date, location, category, and description
3. Click **Post Event** — your event will appear on the events page immediately

### RSVP to an Event
1. Browse events on the **All Events** page or homepage
2. Click the **RSVP** button on any event card
3. Your RSVP is saved and the attendee count updates

### View Your Dashboard
1. Click **Dashboard** in the navigation (you must be logged in)
2. See your stats, events you posted, events you are attending, and recent activity

### Search & Filter
- Use the **search bar** in the header to find events by keyword
- Use the **category links** on the homepage or events page to filter by type

## 📁 Project Structure
```
campus-event-hub/
├── app.py                  # Main Flask application and routes
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── static/
│   ├── main.css            # Custom styles
│   └── images/             # Slideshow images
└── templates/
    ├── base.html           # Shared layout
    ├── home.html           # Homepage
    ├── events.html         # All events listing
    ├── post_event.html     # Post a new event
    ├── edit_event.html     # Edit an existing event
    ├── login.html          # Login page
    ├── register.html       # Registration page
    └── dashboard.html      # User dashboard
```

---

## 🔮 Coming in second release candidate

- Email notifications for RSVPs
- Password reset via email
- Event capacity limits
- User profile pages
- Admin moderation panel
- Deployment to Railway (live public URL)

## ⚠️ Known Limitations in first release candidate

- No email functionality yet
- No password reset
- Runs locally only (not yet deployed)
- Images must be added manually to static/images/

## 📬 Contact

For questions about this project, contact: [ruach.deng@emu.edu]
