# 🎯 Quiz Master

A feature-rich, Flask-based web application that provides an interactive quiz platform with user authentication, dynamic question loading, and real-time scoring.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [Contributors](#contributors)
- [License](#license)
- [Contact](#contact)

---

## 🔍 Overview

**Quiz Master** is an interactive web-based quiz application built with Flask. It offers a seamless user experience with authentication, multiple quiz categories, and a competitive leaderboard system. Whether you're testing knowledge or creating educational content, Quiz Master provides a robust platform for quiz management.

---

## ✨ Features

### 🔐 User Authentication
- **Sign Up**: Create new user accounts with secure password handling
- **Login/Logout**: Session-based authentication for secure access
- **User Profiles**: Track individual user performance and history

### 📝 Quiz System
- **Multiple Quiz Categories**: Organize quizzes by topic or difficulty
- **Dynamic Question Loading**: Questions are fetched from the database in real-time
- **Instant Scoring**: Get immediate feedback on quiz performance
- **Progress Tracking**: Monitor your quiz completion and scores

### 🏆 Leaderboard
- **Global Rankings**: See top performers across all quizzes
- **Score Tracking**: Historical score data for all users
- **Competitive Environment**: Motivate users with public rankings

### 📱 Responsive UI
- **Mobile-Friendly**: Fully responsive design that works on all devices
- **Clean Interface**: Intuitive navigation and modern design
- **Cross-Browser Compatible**: Works seamlessly across different browsers

---

## 🛠️ Technologies Used

### Frontend
- **HTML5**: Semantic markup for better accessibility
- **CSS3**: Modern styling and animations
- **JavaScript**: Interactive client-side functionality
- **Bootstrap** *(Optional)*: Responsive grid system and components

### Backend
- **Flask**: Lightweight Python web framework
- **Flask-Login**: User session management
- **Flask-SQLAlchemy**: ORM for database operations
- **Werkzeug**: Password hashing and security utilities

### Database
- **SQLite**: Lightweight, file-based database for development
- Compatible with PostgreSQL/MySQL for production

---

## 📁 Project Structure

```
Quiz-Master/
│
├── app.py                    # Main Flask application
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── tempCodeRunnerFile.py     # Temporary file (can be ignored)
│
├── instance/                 # Instance-specific files
│   └── quiz.db              # SQLite database (auto-generated)
│
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Image assets
│
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── quiz.html            # Quiz interface
│   ├── results.html         # Results page
│   └── leaderboard.html     # Leaderboard page
│
└── __pycache__/             # Python cache files (auto-generated)
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7+** (Python 3.8 or higher recommended)
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **Virtual Environment** (recommended for dependency isolation)

---

## 🚀 Installation

Follow these steps to set up Quiz Master on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/engnaman7752/Quiz-Master.git
```

### 2. Navigate to Project Directory

```bash
cd Quiz-Master
```

### 3. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present, install the following packages manually:

```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

### 6. Initialize the Database

The database will be created automatically when you first run the application. Alternatively, you can initialize it manually:

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 7. Run the Application

```bash
python app.py
```

### 8. Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000/
```

Or, if running on default Flask port:

```
http://127.0.0.1:5000/
```

---

## 💡 Usage

### Getting Started

1. **Register**: Create a new account on the registration page
2. **Login**: Sign in with your credentials
3. **Select Quiz**: Choose from available quiz categories
4. **Take Quiz**: Answer questions within the quiz interface
5. **View Results**: Get instant feedback on your performance
6. **Check Leaderboard**: Compare your scores with other users

### Admin Features *(Coming Soon)*

- Add new quiz categories
- Create and edit questions
- Manage user accounts
- View analytics and statistics

---

## 🔮 Future Improvements

### Planned Features

- **Admin Panel**: Comprehensive dashboard for managing quizzes and users
- **Timer-Based Quizzes**: Implement countdown timers for time-limited challenges
- **API Integration**: Fetch questions from external APIs (e.g., Open Trivia DB)
- **Question Types**: Support for multiple choice, true/false, and fill-in-the-blank
- **Difficulty Levels**: Easy, Medium, and Hard question categorization
- **Quiz History**: Detailed analytics of past quiz attempts
- **Social Features**: Share scores on social media
- **Email Notifications**: Password reset and achievement notifications
- **Dark Mode**: Toggle between light and dark themes
- **Multi-language Support**: Internationalization for global users

---

## 👥 Contributors

- **Naman Jain** - *Lead Developer* - [GitHub](https://github.com/engnaman7752)

Contributions are welcome! Feel free to submit pull requests or open issues.

---

## 📄 License

This project is open-source and available for anyone to use, modify, and distribute. Feel free to contribute and make it better!

---

## 📧 Contact

For queries, suggestions, or contributions:

- **Email**: [2023kuec2073@iiitkota.ac.in](mailto:2023kuec2073@iiitkota.ac.in)
- **GitHub**: [github.com/engnaman7752](https://github.com/engnaman7752)

---

<div align="center">

Made with ❤️ by [Naman Jain](https://github.com/engnaman7752)

⭐ Star this repository if you find it helpful!

</div>