from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import os

app = Flask(__name__)

# Production Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '7af2c690aae6babb4dbae4cb939fa0fd5bccaf86498f1d540390f44d1d2a7cca')

# Database configuration - supports both SQLite (local) and PostgreSQL (production)
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class userdetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(120), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=1)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    chapter = db.relationship('Chapter', backref='quizzes')

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.route('/')
@app.route('/user', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = userdetail.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                if user.role == 'user':
                    return redirect(url_for('userdash', username=username))
                else:
                    return redirect(url_for('admin', username=username))
            else:
                return render_template("user.html", error="Incorrect password!")
        else:
            return render_template("user.html", error="Username does not exist! Register first.")
    return render_template("user.html", error=False)

@app.route('/newuser', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        dob_string = request.form['dob']
        dob = datetime.strptime(dob_string, '%Y-%m-%d').date()
        qualification = request.form['qualification']
        role = request.form['role']
        existing_user = userdetail.query.filter_by(username=username).first()
        if existing_user:
            return render_template('newuser.html', error="Username already exists! Please use a different one.")
        new_user = userdetail(name=name, username=username, password=password, dob=dob, qualification=qualification, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('newuser.html', error=False)

@app.route('/userdash/<username>')
def userdash(username):
    user = userdetail.query.filter_by(username=username).first()
    if not user:
        return "User not found!", 404
    return render_template("userdash.html", n=user.name)

@app.route('/admin/<username>')
def admin(username):
    user = userdetail.query.filter_by(username=username).first()
    if not user:
        return "User not found!", 404
    subjects = Subject.query.all()
    return render_template("admin.html", n=user.name, subjects=subjects)

@app.route('/start')
def start():
    return render_template("start.html")

@app.route('/addsubject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))
        return redirect(url_for('admin', username=username))
    return render_template('addsubject.html')

@app.route('/addchapter/<int:subject_id>', methods=['GET', 'POST'])
def addchapter(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        username = session.get('username')
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin', username=username))
    return render_template('addchapter.html', subject=subject)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return "Chapter not found!", 404
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin', username=session.get('username')))

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return "Subject not found!", 404
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin', username=session.get('username')))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return "Chapter not found!", 404
    subject = Subject.query.get(chapter.subject_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        return redirect(url_for('admin', username=session.get('username')))
    return render_template('addchapter.html', chapter=chapter, subject=subject)

@app.route('/quiz/<int:chapter_id>', methods=['GET', 'POST'])
def quiz(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return "Chapter not found!", 404
    questions = Question.query.filter_by(chapter_id=chapter_id).all()
    return render_template('quiz.html', chapter=chapter, questions=questions)

@app.route('/addquestion/<int:chapter_id>', methods=['GET', 'POST'])
def addquestion(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return "Chapter not found", 404
    if request.method == 'POST':
        text = request.form['text']
        title = request.form.get('title', '')
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']
        marks = request.form.get('marks', 1, type=int)
        new_question = Question(title=title, text=text, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=correct_option, marks=marks, chapter_id=chapter_id)
        db.session.add(new_question)
        db.session.commit()
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))
        return redirect(url_for('admin', username=username))
    chapters = Chapter.query.all()
    return render_template('addquestion.html', chapter=chapter, chapters=chapters)

@app.route('/newquiz', methods=['GET', 'POST'])
def new_quiz():
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        quiz_date = request.form['quiz_date']
        duration = request.form['quiz_time']
        total_marks = request.form['quiz_marks']
        if not chapter_id or not quiz_date or not duration or not total_marks:
            return render_template('NewQuiz.html', error="All fields are required!")
        new_quiz = Quiz(chapter_id=chapter_id, quiz_date=datetime.strptime(quiz_date, '%Y-%m-%d').date(), duration=int(duration), total_marks=int(total_marks))
        db.session.add(new_quiz)
        db.session.commit()
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))
        return redirect(url_for('admin', username=username))
    chapters = Chapter.query.all()
    return render_template('NewQuiz.html', chapters=chapters, error=None)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
