# Campus Event Hub
Campus Event Hub is a full-stack web application designed to help EMU students discover, organize, and engage with campus activities in one centralized platform. Students can create events, RSVP to upcoming activities, manage their personal schedules, and stay connected with their campus community through a responsive interface.

The platform was developed using the Flask framework with a PostgreSQL database deployed on Railway for production hosting. It combines secure user authentication, dynamic event management, and a clean modern UI to deliver a complete campus event experience.

# Production Deployment
 Hosted on Railway
 PostgreSQL database integration enabled
 
# Live URL: 
https://campus-event-hub.up.railway.app/

# Features
# User Authentication
  Secure user registration and login
  Password hashing using Werkzeug security
  Session-based authentication with Flask-Login
  CSRF protection with Flask-WTF

# Event Management
   Create new campus events
   Edit and delete personal events
   Event ownership protection
   Event categorization system

# RSVP System
   RSVP to upcoming events
   Cancel RSVPs anytime
   Live attendee counts
   Personalized RSVP tracking
   
# Search & Filtering
 Search events by:
    Title
    Description
    Location
 Filter events by category
 Separate Upcoming and Past event tabs

# User Dashboard
  Personal event statistics
  RSVP activity tracking
  Upcoming event overview
  Recent activity feed
  Organizer insights
  
# Responsive UI
  Modern responsive design
  Jinja2 templating
  Custom styling with Pico CSS
  Interactive homepage slideshow

# Tech Stack
# Backend
  Python
  Flask
  Flask-SQLAlchemy
  Flask-Migrate
  Flask-Login
  Flask-WTF
  
# Database
  PostgreSQL (Production)
  SQLite (Local Development)
  
# Frontend
  HTML5
  Pico CSS
  Jinja2 Templates
  JavaScript

# Deployment & Hosting
  Railway
  PostgreSQL on Railway
  Gunicorn
  
# Application Highlights
# Dynamic Event Dashboard
The dashboard provides users with:
  Event analytics
  RSVP tracking
  Personal activity feed
  Upcoming event reminders
  Event management controls

# Event Discovery System
Students can:
  Browse all campus events
  Search by keywords
  Filter by categories
  View upcoming and past events

# Secure Production Configuration
The application includes:
  Environment variable management
  Secure session cookies
  CSRF protection
  Proxy handling for Railway deployment
  PostgreSQL production configuration
  
# Installation & Local Setup
# Prerequisites
  Python 3.9+
  Git 
  
# 1. Clone the Repository
bash
git clone https://github.com/Ruach-Deng/Campus-Event-Hub.git
cd Campus-Event-Hub

# 2. Create a Virtual Environment
# Windows
 bash
python -m venv venv
venv\Scripts\activate

# Mac/Linux
bash
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
bash
pip install -r requirements.txt

# 4. Configure Environment Variables
Create a `.env` file in the project root:
env
SECRET_KEY=your_secret_key_here
DATABASE_URL=your_postgresql_database_url

# 5. Initialize the Database
python
from app import db
db.create_all()
exit()

# 6. Run the Application
bash
flask run

Open your browser and visit:
http://127.0.0.1:5000

# Railway Deployment
This project is fully deployed on Railway using PostgreSQL.

# Deployment Features
  Automatic deployments from GitHub
  Managed PostgreSQL database
  Environment variable configuration
  HTTPS enabled
  Production-ready Flask configuration

# Production Environment Variables
env
SECRET_KEY=your_secret_key
DATABASE_URL=your_railway_postgresql_url

# Project Structure

Campus-Event-Hub/
│
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── runtime.txt
├── .env
│
├── static/
│   ├── main.css
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── events.html
│   ├── event_detail.html
│   ├── post_event.html
│   ├── edit_event.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── 404.html
│   └── 500.html
│
└── migrations/

# Event Categories
The platform currently supports:
  Academics
  Sports
  Social
  Clubs
  Workshop 
  
# Security Features
  Password hashing
  CSRF protection
  Secure session cookies
  Input validation
  Ownership authorization checks
  Protected authenticated routes
  
# Future Improvements

# Planned Features
  Email notifications
  Password reset system
  User profile customization
  Event image uploads
  Event capacity limits
  Admin moderation dashboard
  Real-time notifications
  Comment system
  Mobile app support 
  
# Known Limitations
  No email notification system yet
  No image upload support
  No admin moderation panel
  Limited profile customization

# Author
Developed by Ruach Deng 

# Contact
For questions, feedback, or collaboration opportunities:
Email: ruachdhieu@gmail.com
