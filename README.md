# Campus Event Hub

Campus Event Hub is a full-stack web application created as part of a university web development capstone project. The goal of the project was to build a centralized platform where students can discover campus activities, share events with other students, and keep track of events they plan to attend.

The application was built using Python and Flask, with PostgreSQL used in production and SQLite used during local development. The project is deployed on Railway and includes features such as user authentication, event management, RSVP functionality, dashboards, search, and category filtering.

---

## Live Demo

The application is fully deployed on Railway with a PostgreSQL database.

**Live Website:**
https://campus-event-hub.up.railway.app/
---

## Features

### User Authentication

* Student account registration and login
* Secure password hashing
* Session-based authentication
* Protected user routes

### Event Management

* Create new campus events
* Edit personal events
* Delete events you created
* Organize events by category

### RSVP System

* RSVP to events
* Cancel RSVPs
* Live attendee counts
* Track events you are attending

### Dashboard

* Personal dashboard for each user
* View posted events
* View RSVP activity
* Event statistics and activity feed

### Event Discovery

* Browse all campus events
* Search events by keyword
* Filter events by category
* View upcoming and past events

### Responsive UI

* Mobile-friendly layout
* Custom styling with Pico CSS
* Dynamic templates using Jinja2

---

## Technologies Used

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-Login
* Flask-WTF

### Frontend

* HTML
* CSS
* Pico CSS
* JavaScript
* Jinja2 Templates

### Database

* PostgreSQL (Production)
* SQLite (Local Development)

### Deployment

* Railway
* Gunicorn

---

## Installation & Setup

### Requirements

* Python 3.9+
* Visual Studio Code
* Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/Ruach-Deng/Campus-Event-Hub

cd Campus-Event-Hub
```

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

#### Mac/Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

---

### 5. Set Up the Database

```python
from app import db
db.create_all()
exit()
```

---

### 6. Run the Application

```bash
flask run
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Project Structure

```text
Campus-Event-Hub/
│
├── app.py
├── requirements.txt
├── README.md
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
```

---

## Event Categories

The platform currently supports:

* Academics
* Sports
* Social
* Clubs
* Workshop

---

## Security Features

* Password hashing
* CSRF protection
* Secure session cookies
* Input validation
* User ownership checks for editing and deleting events

---

## Future Improvements

Some features planned for future updates include:

* Email notifications
* Password reset functionality
* User profile customization
* Event image uploads
* Event capacity limits
* Admin moderation panel
* Real-time notifications

---

## Known Limitations

* No password reset system yet
* No email notifications
* No event image upload feature
* Limited user profile customization

---

## Screenshots

You can add screenshots here for:

* Homepage
* Dashboard
* Events page
* RSVP functionality
* User dashboard

---

## Author

Developed by Ruach Deng

---

## Contact

For questions or feedback:

Email: [ruachdhieu@gmail.com](mailto:ruachdhieu@gmail.com)
